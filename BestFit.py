import numpy as np
import matplotlib.pyplot as plt

def wave2RV(Wave,rest_wavelength,RV_BP):
    c = 299792458
    rest_wavelength = rest_wavelength*(RV_BP*1.e3)/c + rest_wavelength # Convert to beta pic reference frame
    delta_wavelength = Wave-rest_wavelength
    RV = ((delta_wavelength/rest_wavelength)*c)/1.e3	# km/s
    return RV

def Bin_data(x,y1,e1,bin_pnts):
    bin_size    = int(len(x)/bin_pnts)
    bins        = np.linspace(x[0], x[-1], bin_size)
    digitized   = np.digitize(x, bins)
    bin_y       = np.array([y1[digitized == i].mean() for i in range(0, len(bins))])
    bin_e       = np.array([e1[digitized == i].mean() for i in range(0, len(bins))])
    return bins, bin_y, bin_e/np.sqrt(bin_pnts)

def main():  

    dat_directory = "/home/paw/science/betapic/data/HST/dat/" 

    v,f_star,f_abs_ism,f_abs_bp,f_after_fit = np.genfromtxt(dat_directory+'Ly_Fit.dat',unpack=True)
    W_cut, F_cut, E_cut = np.genfromtxt(dat_directory+'Ly-alpha_no_AG_2016_06_23.txt',skip_header=500,unpack=True)      
    
    Wo, Fo, Eo      = np.genfromtxt(dat_directory+'Ly_sky_subtracted_no_central_data_2016_06_21.txt',unpack=True)
    W, F, E         = np.genfromtxt(dat_directory+'Ly_sky_subtracted_no_central_data_2016_06_21.txt',unpack=True,skip_header=8980,skip_footer= 7110)

    LyA         = 1215.6702
    RefRV       = 0     # Set to 0 km/s and not 20.5 km/s because the variable v is already shifted by 20.5 km/s from LyFit.py
    bin_pnts    = 5
    
    RV      = wave2RV(W,LyA,RefRV)
    RVo     = wave2RV(Wo,LyA,RefRV)
    RV_cut  = wave2RV(W_cut,LyA,RefRV)
    
    fig = plt.figure(figsize=(6,5))
    fontlabel_size  = 18
    tick_size       = 18
    params = {'backend': 'wxAgg', 'lines.markersize' : 2, 'axes.labelsize': fontlabel_size, 'font.size': fontlabel_size, 'legend.fontsize': 15, 'xtick.labelsize': tick_size, 'ytick.labelsize': tick_size, 'text.usetex': True}
    plt.rcParams.update(params)
    plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
    plt.rcParams['text.usetex'] = True
    plt.rcParams['text.latex.unicode'] = True    


    RVb, Fb, Eb             =   Bin_data(RV,F,E,bin_pnts)
    RVob, Fob, Eob          =   Bin_data(RVo,Fo,Eo,bin_pnts)
    RVb_cut, Fb_cut, Eb_cut =   Bin_data(RV_cut,F_cut,E_cut,bin_pnts)

    plt.plot(v,f_star,lw=3,color='gray',label=r'$\beta$ Pictoris')
    plt.plot(v,f_abs_ism,lw=1.2,color='#FFA500',label=r'ISM')
    plt.plot(v,f_abs_bp,lw=1.2,color='#0386ff',label=r'Gas disk')
    plt.plot(v,f_after_fit,lw=3,color='#FF281C',label=r'Best fit')

    plt.errorbar(RVb_cut,Fb_cut,yerr=Eb_cut,fmt=None,ecolor='black',zorder=3)
    plt.scatter(RVb_cut,Fb_cut, marker='o', edgecolor="black",color='white',zorder=3,label=r'Method 1')
    plt.errorbar(RVb,Fb,yerr=Eb,fmt=None,ecolor='black',zorder=3)
    plt.scatter(RVb,Fb, marker='o', color='k',zorder=3,label=r'Method 2')

    plt.text(400,4.2e-14,r'$\mathrm{O\,V}$',va='center')
    plt.plot([450,550],[4e-14,3e-14],color="black")
    
    plt.xlabel(r'Radial Velocity [km/s]')
    plt.ylabel('Flux (erg/s/cm$^2$/\AA)')

    #plt.xlim(-740,413)
    #plt.ylim(-2.0e-14,6.0e-14)

    plt.xlim(-600,600)
    plt.ylim(-2.5e-14,7.0e-14)
    #plt.ylim(-7.5e-14,7.0e-14)
    #plt.legend(loc='upper left', numpoints=1)
    fig.tight_layout()
    #plt.savefig('../plots/Ly_alpha.pdf', bbox_inches='tight', pad_inches=0.1,dpi=300)
    plt.show()



if __name__ == '__main__':
    main()

