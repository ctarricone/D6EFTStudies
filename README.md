# D6EFTStudies

EFT studies with Dim6 Warsaw basis

## madgraph_model

Modification to the existing SMEFTSim () Madgraph model used for the generation of events.
To produce a sample:
  * to prepare the environment
    on lxplus is to use [LCG environments](http://lcginfo.cern.ch/release_packages/x86_64-centos7-gcc62-opt/96/),
    for example (this alredy has a version of lhapdf as well):
    ```
    source /cvmfs/sft.cern.ch/lcg/views/LCG_96/x86_64-centos7-gcc8-opt/setup.sh 
    ``` 
  * change the location of the pdf data cards
    ``` 
    export LHAPDF_DATA_PATH=/cvmfs/sft.cern.ch/lcg/external/lhapdfsets/current/
    export LHAPDF_DATA_PATH=/cvmfs/sft.cern.ch/lcg/views/LCG_96/x86_64-centos7-gcc8-opt/share/LHAPDF/:$LHAPDF_DATA_PATH
    ``` 
  * clone this package in your local area
      ```
      git clone https://github.com/UniMiBAnalyses/D6EFTStudies
      ```
  * download a Madgraph release and the existing SMEFTSim model:
    ```
    wget https://cms-project-generators.web.cern.ch/cms-project-generators/MG5_aMC_v2.6.5.tar.gz
    tar xzf MG5_aMC_v2.6.5.tar.gz
    cd MG5_aMC_v2_6_5/models
    wget http://feynrules.irmp.ucl.ac.be/raw-attachment/wiki/SMEFT/SMEFTsim_A_U35_MwScheme_UFO_v2.1.tar.gz
    tar xzf SMEFTsim_A_U35_MwScheme_UFO_v2.1.tar.gz
    ```
  * copy in the model folder the additional files present in the D6EFTStudies project, 
    from the right folder depending on the version of the UFO (old or v3, for now old):
    ```
    cp ../../D6EFTStudies/madgraph_model/old/* .
    ```
  * trivial examples of Madgraph syntax can be found [here](https://www.niu.edu/spmartin/madgraph/madsyntax.html)
  * Go to the D6EFT models folder and prepare the Madgraph commands. Have a look at the commands, as you will have to copy paste them.
    ```
    cd ../../D6EFTStudies/generation
    cp /afs/cern.ch/user/c/covarell/public/forGiacomo/create1Dfolders_ZZ2e2mu.py .
    python /afs/cern.ch/user/c/covarell/public/forGiacomo/create1Dfolders_ZZ2e2mu.py
    more launch_ZZ2e2mu_cW_*.txt
    ```
    This creates 3 files with 3 lines each that you will use in the next step. One file is for Linear, one for Quadratic, one for SM.
  * Go back in the Madgraph folder and copy the run_card.
    ```
    cd ../../MG5_aMC_v2_6_5
    cp /afs/cern.ch/user/c/covarell/public/forGiacomo/run_card.dat Template/LO/Cards/.
    ```  
  * Launch MadGraph:
    ```
    ./bin/mg5_aMC
    ```
    Now type in the strings obtained two steps ago. They should look something like:
    ```
    import model SMEFTsim_A_U35_MwScheme_UFO_v2_1-cW_massless
    generate p p > e+ e- mu- mu+ j j QCD=0 NP=1 NP^2==2 SMHLOOP=0
    output ZZ2e2mu_cW_QU
    quit
    ```
    Now you can gon directly to the generation step below.
    <details><summary>If you want more details about what's happening under the hood:</summary>
<p>

    
    Example of generation of VBF Higgs > WW > fully leptonic.
    The following syntax allows for having EFT entering both in the production
    and decay vertices of the Higgs boson, 
    while it remains not present in the W decays.
      * NB1 with the W decay, no restrictions on NP^2 are accepted by Madgraph apparently
      * NB2 SMHLOOP not zero turns on loops coupling with gluons and bosons,
            hence one should most probably turn it off with no expected big impact,
            as its impact is O(alpha^8)
    ```
    ./bin/mg5_aMC
    import model SMEFTsim_A_U35_MwScheme_UFO_v2_1-cHW_massless
    define q = u c d s u~ c~ d~ s~
    generate p p > q q W+ W- QCD=0 SMHLOOP=0 NP=1, W+ > l+ vl, W- > l- vl~ 
    output VBFHWW_RcHW_WWdecay_fs
    quit
    ```
    One operator of interest which enters in the W decay is Hl3, 
    therefore for productions involving that operator
    one needs to generate the full VBS process:
    ```
    working on it
    ```
The comments issued in the Madgraph shell correspond to the model used, 
the process generated, the type of generation:
  * the model used for the generation is issued with the command `import`, 
    which takes as an argument the model name ad possible restrictions,
    as coded in restriction files. 
    In the example, the model is the one contained in the folder `SMEFTsim_A_U35_MwScheme_UFO_v2_1`,
    while the restriction is the one in the file `restrict_cW_massless.dat`.
    The restriction files present in the D6EFTStudies project 
    produce events with massless light leptons and quarks,
    diagonal CKM matrix and rigorously zero value for all the Wilson coefficients, 
    but the one present in the file name.
  * the restriction `restrict_VBS_massless.dat` allows to modify cW, cHW, cHDD, cHbox, cHB, cHWB, cll, cHl3, 
    which are the ones marked as relevant for TGC/QGC and hVV in I. Brivio sildes at 19/01/2019 VBSCan WG1 meeting.
  * the process is generated according to the Madgraph syntax. In particular:
    * NP=1 means that no more than a single BSM operator is introduced in each diagram
    * NP^2==1, when present, means that only the interference is calculated
    * NP^2==2, when present, means that only the squared bsm part is calculated
  * the default run_card.dat produced by Madgraph may be changed by modifying the file
    ```Template/LO/Cards/run_card.dat``` in the Madgraph folder
  * besides the interactive operation, Madgraph may be used with instruction scripts, containing for example:
    ```
    import model SMEFTsim_A_U35_MwScheme_UFO_v3_1-cW_massless
    generate p p > e+ ve mu- vm~ NP=1 NP^2==1
    add process p p > e- ve~ mu+ vm NP=1 NP^2==1
    output WW_LI
    ```  
  * the script ```create1Dfolders.py``` generates the Madgpraph code for the event generation
    with one Wilson coefficient different from zero, for the linear and quadratic EFT terms,
    according to the list of operators switched on in the script.
  * the script ```create2Dfolders.py``` generates the Madgpraph code for the event generation
    with two Wilson coefficients interfering between each other,
    according to the list of operators switched on in the script.
</p>
</details>
## generation

Scripts to submit jobs to condor, for the generation of events in Madgraph.
To submit a job:
  * copy the folder present in the Madgraph directory in this folder:
   ```
   cp -r ../../MG5_aMC_v2_6_0/SSeu_RcW_test .
   ```
  * run the submission script
   ```
   ./submit.py SSeu_RcW_test
   ```
Config file examples can be found in the subfolders `generation/SSeu_RcW/Cards/`, 
`generation/SSeu_RcW_int/Cards/`, `generation/SSeu_RcW_bsm/Cards/`, 
where the `param_card.dat`, `run_card.dat` and `proc_card.dat` examples for same-sign WW
and `cW` non zero are reported. The three folders refer to the SM case, the interference between SM and BSM
and the BSM case respectively. 
Operators of interest are listed [here](https://www.dropbox.com/s/e5yvvzzo98bwdg3/2019-06-ongoing_dim6.pdf?dl=0)
  * The script ```postProcess.py``` takes as input a ```*_results``` folder,
    controls some basic parameters for the success of the generation,
    unpacks the LHE files, creates a summary of the run,
    and cleans the folder from unnecessary log files when called with the ```clean``` option
    (keeping those of failed jobs).
    It also creates the input cfg file for ```read_03.cpp```,
    adding the cfg file to the folder itself

## analysis

  * `read_02.cpp` reads LHE files and produces sets of histograms, NOT MAINTAINED
  * `read_03.cpp` reads LHE files and produces sets of ntuples
    * takes as input argument a config file: ```./read_03 cfg/ntuple_SSeu_RcW_0p3.cfg```
    * an additional argument sets the total number of events read per sample: ```./read_03 cfg/ntuple_SSeu_RcW_0p3.cfg 100```
    * all variables used later on are created here, for the time being
  * `checkEntries.cpp` checks the number of entries of all ntuples stored in a root file

<!-- ### fit

This is where the plain ntuples get analysed and fits performed.
 -->
## DatacarCreator

### datacard\_creator\_2.cpp

The code has been mostly taken from ```datacard_creator.cpp```. 
Fragmented in subfunctions implemented in ```dcutils.*```,
reads a config file containing the list of variables to be studied,
the selections to be applied,
the files to be read and some detailed configuration parameters
  * files have to be produced with ```read_03.cpp```, 
    which is where variables are built. 
    If a new variable is needed,
    for the time being a new run of ```read_03.cpp``` is required.
  * for each variable as an input in the cfg file,   
    ```datacard_creator_2.cpp``` produces a pair of files:
    a root file containing histograms and a datacard for Combine.
  * In the folder where datacards are stored, a shell script gets created,
    that contains the commands to be run to create the roofit workspaces
    needed by Combine, as well as one to issue the combine fit.
    The script should be sourced from an environment built according to the indications
    present in EFT/Fit.
    Single .sub and .sh files to be launched with condor get created as well.

### datacard\_TwoOp\_creator\_2.cpp

  * Prepares the combine datacards for 2D ```combine``` fits.
  * In the folder where datacards are stored, a shell script gets created,
    that contains the commands to be run to create the roofit workspaces
    needed by Combine, as well as one to issue the combine fit.
    The script should be sourced from an environment built according to the indications
    present in EFT/Fit.
    Single .sub and .sh files to be launched with condor get created as well.

### Condor submission

To submit to condor the creation of the workspaces and the ```combine``` fitting procedure,
launch ```condor_submit``` with as argument the submit\*.sub file of interest
from the created datacard folders.
Once a set of folders have been created by ```datacard_creator_2``` or ```datacard_twoOp_creator_2```,
once can submit all jobs at once like this:
```for fil in `find . -maxdepth 2 -name "submit*ub" | grep SSWW` ; do condor_submit $fil ; done```
In this case, all files that have the name like ```submit*ub``` 
and are in a folder which has ```SSWW``` in its name
will be sent to condor.

### read_results.cpp

Runs over the rootfiles resulting from the ```combine``` fits and produces 1D likelihood scans


## Fits with Combine

Instructions on how to install and use combine for likelihood scan.
  * The reference for the building of anomalous coupling analytic fitting 
    are [here](https://github.com/amassiro/AnalyticAnomalousCoupling).
  * A Combine tutorial can be found [here](https://indico.cern.ch/event/859454/)

You need to be either on MiB cluster/virgilio 
(read the message after logging in on what to source to be able to use cmssw) 
or on lxplus.

  * The Combine repository and some instruction are [here](https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/tree/master)
  * The main Combine documentation is [here](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/)

The installation is needed also when using the scripts created by ```datacard*_creator_2```, 
which takes care of the steps C and D.

### A) install Combine

Prepare a CMSSW release where to install combine, 
which sets the proper compiling environment with a consistent set of libraries
to be linked in the compilation process
(the command ```cmsenv``` sets all the shell environment variables needed for compiling and running
once and for all).
Since the CMSSW and Combine code is taken from a Git repository, it's suggested to install it
*outside* of the EFT folder.

    cmsrel CMSSW_10_2_13
    cd CMSSW_10_2_13/src
    cmsenv

Download the Combine tool inside the CMSSW release environment and enter the subfolder:

    git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit

Go to the Combine subfolder, 
and get the right stable version of Combine
compatible with our setup:
    
    cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
    git fetch origin
    git checkout v8.0.1

Compile combine with the ```scramv1``` compiling tool of the CMS software

    scramv1 b clean; scramv1 b

### B) install the fitting model

Download our fitting model and compile it

    cd $CMSSW_BASE/src/HiggsAnalysis
    git clone git@github.com:amassiro/AnalyticAnomalousCoupling.git
    scramv1 b -j 20
    
### C) generate a RooFit workspace starting from the datacards

The workspace is the RooFit container that holds all the information needed by Combine di perform fits.
THe following script creates the workspace starting from the txt and root files 
produced by datacard_creator and datacard_creator_2
of EFT/DatacardCreator.

    text2workspace.py datacard.txt \
                      -P HiggsAnalysis.AnalyticAnomalousCoupling.AnomalousCoupling:analiticAnomalousCoupling \
                      --PO=k_my_1,r \
                      -o  model_test.root   
where:

| option                                        | meaning                                                                    |
| --------------------------------------------- | -------------------------------------------------------------------------- |
| ```-P PHYSMODEL```                            | Physics model to use. It should be in the form (module name):(object name) |
| ```HiggsAnalysis.AnalyticAnomalousCoupling``` | module name of the physics model, it's a folder                            |
| ```analiticAnomalousCoupling```               | object name of the physics model                                           |
| ```--PO = k_my_1,r```                           | define the physics observables to be ```k_my_1``` and ```r```                |
| ```-o model_test.root```                      | filename of the workspace created                                          |

The module ```HiggsAnalysis.AnalyticAnomalousCoupling``` is actually implemented in "
  * ```HiggsAnalysis/AnalyticAnomalousCoupling/python/AnomalousCoupling.py```: old version
  * ```HiggsAnalysis/AnalyticAnomalousCoupling/python/AnomalousCouplingTwoOp.py```:
    version with one single Wilson coefficient free to float 
  * ```HiggsAnalysis/AnalyticAnomalousCoupling/python/AnomalousCouplingOneOp.py```:
    version with two Wilson coefficients free to float
  * ```HiggsAnalysis/AnalyticAnomalousCoupling/python/AnomalousCouplingEFT.py```:
    version with all SMEFTSim Wilson coefficients free to float.
**NB** the root file is searched for in the subfolder indicated in the txt file, 
       by the ```text2workspace.py``` script.
The workspace created can be printed for inspection:

    root -b model_test.root
    w->Print ()

When using datacard_creator_2, two shell script are also created,
that contain the commands to be issued to actually create the workspaces, 
and that run Combine to perform the fits.
Those scripts use the ```AnomalousCouplingEFT``` of the EFT model.

### D) fit

Simulate with k_my_1 set to 1 and r=1

    combine -M MultiDimFit model_test.root             \
            --algo=grid --points 120  -m 125           \
            -t -1 --expectSignal=1                     \
            --redefineSignalPOIs k_my_1                  \
            --freezeParameters r --setParameters r=1   \ 
            --setParameterRanges k_my_1=-20,20           \
            --verbose -1

Where:

| option                                 | meaning                                                                                          |
| -------------------------------------- | ------------------------------------------------------------------------------------------------ |
| ```-M MultiDimFit```                   | use the method ```MultiDimFit``` to extract upper limits                                         |
| ```--algo=grid```                      | choose the algorithm ```grid``` to compute uncertainties                                         |
| ```--points 120```                     | set to 120 the number of points in *DOING SOMETHING*                                             |
| ```-m 125```                           | set the Higgs boson mass to 125 GeV                                                              |
| ```-t -1```                            | number of Toy MC extractions                                                                     |
| ```--expectSignal=1```                 | generate *signal* toys instead of background ones, with the specified signal strength.           |
| ```--redefineSignalPOIs k_my_1```        | set ```k_my_1``` as the only physics observable in the fit                                         |
| ```--freezeParameters r```             | the parameter ```r``` has a value which will not change in the fit                               |
| ```--setParameters r=1```              | the value to which ```r``` is frozen                                                             |
| ```--setParameterRanges k_my_1=-20,20``` | range of variability of the free parameter considered in the fit                                 |
| ```--verbose -1```                     | verbosity set to minimum                                                                         |

To simulate "sm" part, k_my_1 == 0 (this is how we simulate the expected result with "sm") :
        
    combine -M MultiDimFit model_test.root                  \           
            --algo=grid --points 120  -m 125                \              
            -t -1 --expectSignal=1                          \      
            --redefineSignalPOIs k_my_1                       \     
            --freezeParameters r --setParameters r=1,k_my_1=0 \                             
            --setParameterRanges k_my_1=-20,20
    
### E) plot the profile likelihood obtained

    cd $CMSSW_BASE/src/HiggsAnalysis/AnalyticAnomalousCoupling/test/
    root -l higgsCombineTest.MultiDimFit.mH125.root  \
            higgsCombineTest.MultiDimFit.mH125.root draw.cxx


## PostPlots

### ```read_results.cpp```

Performes the detailed inspection of each single operator for 1D scans, 
produces the likelihood scans,
calculates the crossing points with the horisontal thresholds
for 1sigma and 2sigma, plots all the results 
and produces a summary txt CSV (comma-separated values) file
containing the scan of all operators and variables considered
in the generation campaign.
Takes as input the cfg file fed to DatacardCreator
and optionally the folder where the \*result folder are saved.

### ```read_results_2D.cpp```

Performes the detailed inspection of each single operator for 2D scans, 
calculates the crossing intersections with the horisontal thresholds
for 1sigma and 2sigma, 
plots the obtained contours ranked in area for the 1sigma CL.
Takes as input the cfg file fed to DatacardCreator
and optionally the folder where the \*result folder are saved.

### ```summaryPlots.cpp```

Compares two different set of results
(for example SSWW VBS and inclusive prodcution),
taking as input the output CSV files of ```read_results.cpp```.

## useful commands and links

  * unzip madgraph results within a folder
   ```
   for fil in  `find  . -name "*gz"` ; do gunzip $fil ; done
   ```
  * prepare list of lhe files for cfg files (rem unalias ls)
   ```
   find . -name "*lhe" | sed -e s%\.%`pwd`% | tr "\n" ","
   ```
  * calculate the cross-section of the sample from the generated events, in the generation folder:
   ```
   ./postProcess.py [folder containing the job outputs and lhe files]
   ```
  * Madgraph totorial [here](https://indico.cern.ch/event/555228/sessions/203428/attachments/1315471/1970459/tutorial-CMSandATLAS-2016.pdf)


