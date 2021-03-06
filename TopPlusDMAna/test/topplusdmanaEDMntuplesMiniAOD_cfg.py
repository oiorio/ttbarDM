### *****************************************************************************************
### Usage:
###
### cmsRun topplusdmanaEDMntuples_cfg.py maxEvts=N sample="mySample/sample.root" version="71" outputLabel="myoutput"
###
### Default values for the options are set:
### maxEvts     = -1
### sample      = 'file:/scratch/decosa/ttDM/testSample/tlbsm_53x_v3_mc_10_1_qPV.root'
### outputLabel = 'analysisTTDM.root'
### *****************************************************************************************
import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as opts




### Check whether the jet filter is applied!!!!



options = opts.VarParsing ('analysis')

options.register('maxEvts',
                 -1,# default value: process all events
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.int,
                 'Number of events to process')

options.register('sample',
                 'file:/afs/cern.ch/user/d/decosa/public/forTTDMteam/patTuple_tlbsm_train_tlbsm_71x_v1.root',
#                 'file:/afs/cern.ch/user/d/decosa/public/forTTDMteam/tlbsm_53x_v3_mc_10_1_qPV.root',
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.string,
                 'Sample to analyze')

options.register('version',
                 #'53',
                 '71',
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.string,
                 'ntuple version (53 or 71)')

options.register('outputLabel',
                 'analysisTTDM.root',
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.string,
                 'Output label')

options.register('isData',
                 False,
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.bool,
                 'Is data?')

options.register('miniAOD',
                 False,
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.bool,
                 'miniAOD source')

options.register('LHE',
                 False,
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.bool,
                 'Keep LHEProducts')

options.parseArguments()

if(options.isData):options.LHE = False

    
###inputTag labels
if(options.miniAOD):
    muLabel  = 'slimmedMuons'
    elLabel  = 'slimmedElectrons'
    jetLabel = 'slimmedJets'
    pvLabel  = 'offlineSlimmedPrimaryVertices'
    particleFlowLabel = 'packedPFCandidates'    
    metLabel = 'slimmedMETs'
else:
    muLabel = 'selectedPatMuons'
    elLabel = 'selectedPatElectrons'
    if options.version=="53" :
        jetLabel="goodPatJetsPFlow"
    elif options.version=="71" :
        jetLabel="goodPatJets"
    pvLabel             = "goodOfflinePrimaryVertices"
    particleFlowLabel = "particleFlow"    
    metLabel = 'patMETPF'

triggerResultsLabel = "TriggerResults"
triggerSummaryLabel = "hltTriggerSummaryAOD"
hltMuonFilterLabel       = "hltL1sL1Mu3p5EG12ORL1MuOpenEG12L3Filtered8"
hltPathLabel             = "HLT_Mu8_Ele17_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL"
hltElectronFilterLabel  = "hltL1sL1Mu3p5EG12ORL1MuOpenEG12L3Filtered8"
lheLabel = "source"


    
process = cms.Process("ttDManalysisEDMNtuples")

process.load("FWCore.MessageService.MessageLogger_cfi")
### Output Report
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
### Number of maximum events to process
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvts) )
### Source file
process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
        options.sample
        )
)

process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
from Configuration.AlCa.GlobalTag import GlobalTag as customiseGlobalTag
process.GlobalTag = customiseGlobalTag(process.GlobalTag, globaltag = 'auto:startup_GRun')
process.GlobalTag.connect   = 'frontier://FrontierProd/CMS_COND_31X_GLOBALTAG'
process.GlobalTag.pfnPrefix = cms.untracked.string('frontier://FrontierProd/')
for pset in process.GlobalTag.toGet.value():
    pset.connect = pset.connect.value().replace('frontier://FrontierProd/', 'frontier://FrontierProd/')
    #   Fix for multi-run processing:
    process.GlobalTag.RefreshEachRun = cms.untracked.bool( False )
    process.GlobalTag.ReconnectEachRun = cms.untracked.bool( False )
    

### Selected leptons and jets
process.skimmedPatMuons = cms.EDFilter(
    "PATMuonSelector",
    src = cms.InputTag(muLabel),
    cut = cms.string("pt > 30 && abs(eta) < 2.4")
    )

process.skimmedPatElectrons = cms.EDFilter(
    "PATElectronSelector",
    src = cms.InputTag(elLabel),
    cut = cms.string("pt > 30 && abs(eta) < 2.5")
    )


process.skimmedPatJets = cms.EDFilter(
    "CandViewSelector",
    src = cms.InputTag(jetLabel),
#    src = cms.InputTag("goodPatJetsPFlow"), # 53x
#    src = cms.InputTag("goodPatJets"), # 71x    
    cut = cms.string("pt > 25 && abs(eta) < 4.")
    )


### Asking for at least 2 jets satisfying the selection above 
process.jetFilter = cms.EDFilter("CandViewCountFilter",
    src = cms.InputTag("skimmedPatJets"),
    minNumber = cms.uint32(2),
    filter = cms.bool(True)
)

    
process.muonUserData = cms.EDProducer(
    'MuonUserData',
    muonLabel = cms.InputTag("skimmedPatMuons"),
    pv        = cms.InputTag(pvLabel),
    triggerResults = cms.InputTag(triggerResultsLabel),
    triggerSummary = cms.InputTag(triggerSummaryLabel),
    hltMuonFilter  = cms.InputTag(hltMuonFilterLabel),
    hltPath             = cms.string(hltPathLabel),
)


    
    
process.electronUserData = cms.EDProducer(
    'ElectronUserData',
    eleLabel = cms.InputTag("skimmedPatElectrons"),
    pv        = cms.InputTag(pvLabel),
    triggerResults = cms.InputTag(triggerResultsLabel),
    triggerSummary = cms.InputTag(triggerSummaryLabel),
    hltElectronFilter  = cms.InputTag(hltElectronFilterLabel),  ##trigger matching code to be fixed!
    hltPath             = cms.string(hltPathLabel)
)



from PhysicsTools.CandAlgos.EventShapeVars_cff import *
process.eventShapePFVars = pfEventShapeVars.clone()
process.eventShapePFVars.src = cms.InputTag(particleFlowLabel)

process.eventShapePFJetVars = pfEventShapeVars.clone()
process.eventShapePFJetVars.src = cms.InputTag("skimmedPatJets")

process.centrality = cms.EDProducer("CentralityUserData",
   src = cms.InputTag("skimmedPatJets")
)                                    

### Including ntuplizer 
process.load("ttbarDM.TopPlusDMAna.topplusdmedmNtuples_cff")





### definition of Analysis sequence
process.analysisPath = cms.Path(
    process.skimmedPatElectrons +
    process.skimmedPatMuons +
    process.skimmedPatJets +
    process.eventShapePFVars +
    process.eventShapePFJetVars +
    process.centrality
)

#process.analysisPath+=process.jetFilter

process.met.src = cms.InputTag(metLabel)

#process.analysisPath+=process.muonUserData
process.analysisPath+=process.electronUserData
process.analysisPath+=process.genPart
#process.analysisPath+=process.muons
process.analysisPath+=process.electrons
process.analysisPath+=process.jets
process.analysisPath+=process.met
process.analysisPath+=process.eventInfo

### Creating the filter path to use in order to select events
process.filterPath = cms.Path(
    process.jetFilter
    )


### keep info from LHEProducts if they are stored in PatTuples
if(options.LHE):
    process.LHEUserData = cms.EDProducer("LHEUserData",
        lheLabel = cms.InputTag(lheLabel)
        )
    process.analysisPath+=process.LHEUserData
    process.edmNtuplesOut.outputCommand+=(' *_LHE*_*_*')

### end LHE products     


process.edmNtuplesOut.SelectEvents = cms.untracked.PSet(
    SelectEvents = cms.vstring('filterPath')
    )

process.fullPath = cms.Schedule(
    process.analysisPath,
    process.filterPath
    )

process.endPath = cms.EndPath(process.edmNtuplesOut)

## process.outpath = cms.Schedule(
##     process.analysisPath,
##     process.endPath
##     )
