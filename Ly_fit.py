import numpy as np
import matplotlib.pyplot as plt
import sys

def voigt_wofz(a, u):
    """ Compute the Voigt function using Scipy's wofz().

    # Code from https://github.com/nhmc/Barak/blob/\
    087602fb372812c0603441ca1ce6820e96963b88/barak/absorb/voigt.py

    Parameters
    ----------
    a: float
      Ratio of Lorentzian to Gaussian linewidths.
    u: array of floats
      The frequency or velocity offsets from the line centre, in units
      of the Gaussian broadening linewidth.

    See the notes for `voigt` for more details.
    """
    try:
         from scipy.special import wofz
    except ImportError:
         s = ("Can't find scipy.special.wofz(), can only calculate Voigt "
              " function for 0 < a < 0.1 (a=%g)" % a)  
         print(s)
    else:
         return wofz(u + 1j * a).real

def absorption(l,v,nh,T,LyA):
    
    # [Hydrogen, Deuterium]
    
    w       = [LyA,1215.3394]
    mass    = [1.,2.]
    fosc    = [0.416,0.416]
    delta   = np.array([0.627e9,0.627e9]) /(4.*np.pi)
    N_col   = np.array([1.,1.5e-5])*10**nh
    c       = 2.99793e14

    for i in range(len(w)):
        b_wid   = np.sqrt((T/mass[i]) + ((v/0.129)**2))
        b       = 4.30136955e-3*b_wid
        dnud    = b*c/w[i]

        xc      = l/(1.+v*1.e9/c)
        v       = 1.e4*abs(((c/xc)-(c/w[i]))/dnud)
        tv      = 1.16117705e-14*N_col[i]*w[i]*fosc[i]/b_wid
        a       = delta[i]/dnud
        hav     = tv*voigt_wofz(a,v)
              
        abs_ism = np.ones(len(hav))
        
        # I am uncertain about the translation from IDL to python here
        # To avoid underflow which occurs when you have exp(small negative number)
        for j in range(len(hav)):
            if hav[j] < 20.:      
                abs_ism[j]  =   abs_ism[j]*np.exp(-hav[j])       
            else:
                abs_ism[j]  =   0.
                
    return abs_ism

def main():    

    W, F, E = np.genfromtxt('Ly-alpha.dat',unpack=True)
    
    ### Parameters ##############################   
    mode    = 'fast'
    
    LyA     =   1215.6737

    # ISM parameters
    v_ism   =   10.0        # RV of the ISM (relative to Heliocentric)      
    nh_ism  =   18.         # Column density ISM
    b_ism   =   7.          # Turbulent velocity
    T_ism   =   7000.       # Temperature of ISM

    # Beta Pic parameters
    v_bp    =   20.5        # RV of the beta Pic (relative to Heliocentric)
    nh_bp   =   18.45       # Column density beta Pic
    b_bp    =   2.          # Turbulent velocity
    T_bp    =   1000.       # Temperture of gas in beta Pic disk

    max_f   =   4.395e-13                    
    dp      =   0.0 
    uf      =   11.
    av      =   8.      

    sigma_kernel    =   7.
    #############################################

    v           =   np.arange(-len(W)/2.,len(W)/2.,1)   # RV values
    l           =   LyA*(1.0 + v/3e5)                   # Corresponding wavengths
    
    # Calculates the ISM absorption
    # see IDL function 'calculate_abs_ism'
    abs_ism =   absorption(l,v_ism,nh_ism,T_ism,LyA)
    abs_bp  =   absorption(l,v_bp,nh_bp,T_bp,LyA)
    
    # LSF
    # Dispersion of the theoretical wavelength range
    # np.roll is equivalent to the IDL shift function
    dl          =   np.mean((l-np.roll(l,1))[1:])
    dwave       =   np.median((W-np.roll(W,1))[1:])     
    kernel      =   v
    kernel      =   np.exp(-kernel**2/2./((sigma_kernel*dwave/dl)**2))
    kernel      =   kernel/np.sum(kernel)
    
    # Double Voigt profile
    delta_lambda=   LyA*(v_bp/3e5)
     
    lambda0     =   LyA                     # Lyman alpha center
    lambda1     =   LyA -dp + delta_lambda  # blue peak center
    lambda2     =   LyA +dp + delta_lambda  # red peak center

    u1          =   uf*(l-lambda1)          # blue peak wavelengths
    u2          =   uf*(l-lambda2)          # red peak wavelengths

    f           =   max_f*(voigt_wofz(av,u1)+voigt_wofz(av,u2))

    # Stellar spectral profile, as seen from Earth
    # after absorption by the ISM and BP CS disk   
    #    -  in (erg cm-2 s-1 A-1)
    f_abs       =   f*abs_ism*abs_bp

    #Stellar spectral profile, after convolution by Hubble LSF 
    #    -  in (erg cm-2 s-1 A-1)
    f_abs_con   =   np.convolve(f_abs,kernel,mode='same')
    
    # Interpolation on COS wavelengths, relative to the star
    f_abs_int   =   np.interp(W,l,f_abs_con)

    # Absorption by beta Pictoris
    f_abs_bp_0  =   f*abs_bp
    f_abs_bp    =   np.convolve(f_abs_bp_0,kernel,mode='same')

    # Absorption by the ISM
    f_abs_ism_0 =   f*abs_ism
    f_abs_ism   =   np.convolve(f_abs_ism_0,kernel,mode='same')

    # Stellar Ly-alpha line
    f_star      =   np.convolve(f,kernel,mode='same')

    # Plot the results
    plt.plot(W,f_abs_int)
    plt.plot(l,f_abs_bp)
    plt.plot(l,f_abs_ism)
    plt.plot(l,f_star,color='red')
    plt.plot(W,F,color='black')

    plt.xlabel(r'Wavelength $\AA$')
    plt.ylabel('Flux')

    plt.xlim(1213,1217.5)
    #plt.ylim(-0.3e-14,5.5e-14)
    plt.show()

if __name__ == '__main__':
    main()