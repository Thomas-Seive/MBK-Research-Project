def axis(arr_in, rad, shell=False, axes_out=False, fix_volume=True, quiet=False):
    import numpy as np
    import scipy.linalg as linalg
    """Compute axis ratios iteratively.

    WORK IN PROGRESS -- Needs to be checked.
    2D VERSION -- Worked on by Thomas Seive. Primary purpose is to calculate
    the ellipticity of a galaxy while only considering one projection (two axes).
    This version cannot make use of the shell feature found in the 3d version
    Here is just a small change to the code to try and test this github push/pull feature
    Here is another line that I've added. Slowly getting the hang of this git stuff!
    Adding this line for the github test on Mac; another test to see if I can add without
    needing to log in to github
    Managed to make a change on my mac and get the change on my pc! Let's do the reverse
    Don't even need to close the file for it to refresh with the new changes! (at least on mac)
    And the same on PC! I can now officially use github to work on my code :-)
    End 2D code//

    May want to add capability to compute axis ratios at multiple
    different radii in one function call (w/ a loop?) 

    See Dubinski & Carlberg (1991) for details

    INPUTS:
    arr_in: array of particle positions, assumed to be centered. A 2D array for the 2D case
    rad: radius to compute axis ratios.  If computing axis ratios in
    shells, rad should be a two-element list / array, with rad[0] =
    inner radius of shell and rad[1] = outer radius of shell.
    Otherwise, rad should be a real number equal to the radius within
    which to compute the axis ratios


    OPTIONAL INPUTS:
    shell=False: by default, compute cumulative axis ratio
    (i.e. for all particles within radius r).  If shell=True, compute
    axis ratio in an ellipsoidal shell instead.
    axes_out=False:  if True, also return principal axes (in ascending order)
    fix_volume=True: keep the volume of the ellipsoid constant while iterating.
    If false, keep the semi-major axis equal to the initial (spherical) search
    radius. This will result in a smaller effective volume.
    quiet=False: if set to true, suppress information that is printed
    on each iteration
    """
    def calc_inertia(arr_in, axrat_in):

        """calculate the modified moment of inertia tensor and get its eigenvalues and eigenvalues"""
        tensor=np.zeros([2,2])
        # given initial values for primary axes, compute ellipsoidal
        # radius of each particle (rp2 is not square rooted because it is squared in the next step, i.e. they cancel)
        rp2=(arr_in[:,0]**2/axrat_in[0]**2 + arr_in[:,1]**2/axrat_in[0]**2) #(Thomas)changed this line
        #made axrat_in call only the [0] element because I will only have one axial ratio to guess

        # construct the moment of inertial tensor to be diagonalized:
        for i in range(2): #(Thomas)changed this line, rp2 is the "a" from the paper
            for j in range(2):
                tensor[i,j]=(arr_in[:,i]*arr_in[:,j]/rp2).sum()
        
        evecs=linalg.eig(tensor)
        
        # return a tuple with eigenvalues and eigenvectors; 
        # eigenvalues=evecs[0], eigenvectors=evecs[1]
        return evecs

    cnt=0
    # initial guess for principal axes:
    evs0=np.array([[1e0,0e0],[0e0, 1e0]]) #(Thomas) changed this line
    # initial guess for axis ratios: 
    axes=np.array([1e0]) #(Thomas) changed this line: only give one initial guess because we are only calculating one 
    #axial ratio
    avdiff=1e0

    rad=np.asarray(rad)
    # ******************************
    # fixed portion of code (From June 8, 2017)
    while avdiff > 0.01:
        axtemp=axes.copy()
        # compute ellipsoidal radius of each particle:  (Thomas)This is a radius for each particle
        dist2=(
               arr_in[:,0]**2/axes[0]**2 +
               arr_in[:,1]**2/axes[0]**2)**0.5
            #(Thomas)Changed the line above
        # find locations of particles between rad[0] and rad[1]
        if not fix_volume:
            r_ell=rad
        else:
            r_ell=(rad**3/axes[0]/axes[0])**(1e0/3e0) #(Thomas): Broke this line so
            #dont use the shells! 
            
 
        # current version keeps volume same as original spherical
        # volume rather than keeping principal axis same as
        # initial radius
        if shell == True:
            locs=((dist2 < r_ell[1]) & 
                  (dist2 > r_ell[0])).nonzero()[0]
        else:
            locs=(dist2 < r_ell).nonzero()[0]

            # ******************************

        # get eigenvectors and eigenvalues.  Note: the inertia tensor
        # is a real symmetric matrix, so the eigenvalues should be real.
        # locs is the location (radius) for particles
        # axtemp is the current axial ratios (q & s) 
        axrat=calc_inertia(arr_in[locs], axtemp)
        if abs(np.imag(axrat[0])).max() > 0.:
            raise ValueError('Error: eigenvalues are not all real!')

        evals=np.real(axrat[0])
        evecs=axrat[1]
        # get axis ratios from eigenvalues: (Thomas) Changed this line; have no third component with which
        # to calculate q and s
        axes=np.sqrt([evals[1]/evals[0] 
                         ])
        # rotate particles (and previous eigenvector array) into new
        # basis:
        arr_in=np.dot(arr_in, evecs)
        evs0=np.dot(evs0, evecs)
        
        # compute difference between current and previous iteration
        # for axis ratios and diagonal of eigenvector matrix
        avd0=abs((axtemp[0]-axes[0])/(axtemp[0]+axes[0]))

        # used to check how close most recent rotation is to zero
        # rotation (i.e. how close evecs is to the identity matrix)
        avd2=2e0-abs(evecs[0,0])-abs(evecs[1,1]) #(Thomas)changed this line
        if quiet == False:
            # print axis ratios relative to major axis
            print ('axis ratios: ', (np.sort(evals/evals.max()))**0.5)
            print ('deviations from previous iteration: ' + \
            '%.*e, %.*e' % (4, avd0, 4, avd2))
            print ('number of particles in shell / sphere: ', np.size(locs))
        avdiff=max(avd0, avd2)
        cnt+=1

    # normalize eigenvalues to largest eigenvalue
    evals=evals/evals.max()
    inds=evals.argsort()
    final_axrats=evals[inds[:2]]**0.5
    print ('number of iterations: ', cnt)
    print ('number of particles in shell / sphere: ', np.size(locs))
    print ('normalized eigenvalues (sorted in ascending order) ' + 
    'and corresponding unit eigenvectors are:')
    print ('%.*f' % (5, evals[inds[0]]), evs0[:,inds[0]])
    print ('%.*f' % (5, evals[inds[1]]), evs0[:,inds[1]])
    #print ('%.*f' % (5, evals[inds[2]]), evs0[:,inds[2]])
    print ('axis ratios: ', final_axrats)
    if axes_out:
        return final_axrats, [evs0[:,inds[0]], evs0[:,inds[1]], evs0[:,inds[2]]]
    else:
        return final_axrats