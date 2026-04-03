import FWCore.ParameterSet.Config as cms

from SRothman.EECs.common_cff import get_producer, get_matched_producer, get_transfer_producer
from SRothman.EECs.common_cff import get_table, get_transfer_table

def setupEEC_data(process,
                  name,
                  recojets,
                  config,
                  whichEEC,
                  verbose=0):
    
    name = name + whichEEC

    setattr(process, name,
        get_producer(config, recojets, whichEEC, 'reco')
    )
    setattr(process, "Reco%sTable"%name,
        get_table(config, name, whichEEC, 'reco')
    )

    setattr(process, "Reco%sTask"%name,
        cms.Task(
            getattr(process, name),
            getattr(process, "Reco%sTable"%name),
        )
    )
    process.schedule.associate(getattr(process, "Reco%sTask"%name))

    return process

def setupEEC_MC(process, 
                name,
                genMatch,
                genjets, 
                recojets,
                config,
                whichEEC,
                verbose=0):

    name = name+whichEEC

    setattr(process, name,
        get_matched_producer(config, recojets, genMatch, whichEEC, 'reco')
    )
    setattr(process, "Reco%sTable"%name,
        get_table(config, name, whichEEC, 'reco')
    )
    setattr(process, "UnmatchedReco%sTable"%name,
        get_table(config, name, whichEEC, 'unmatchedReco')
    )

    setattr(process, '%sRecoTask'%name, cms.Task(
        getattr(process,'%s'%name),
        getattr(process, 'Reco%sTable'%name),
        getattr(process, 'UnmatchedReco%sTable'%name),
    ))
    process.schedule.associate(getattr(process, '%sRecoTask'%name))


    setattr(process, 'Gen%s'%name,
        get_transfer_producer(
            config,
            genjets, 
            recojets, 
            genMatch,
            whichEEC
        )
    )   
    setattr(process, 'Gen%sTable'%name,
        get_table(config, 'Gen%s'%name, whichEEC, 'gen')
    )
    setattr(process, 'UnmatchedGen%sTable'%name,
        get_table(config, 'Gen%s'%name, whichEEC, 'unmatchedGen')
    )
    setattr(process,'Transfer%sTable'%name,
        get_transfer_table(config, 'Gen%s'%name, whichEEC)
    )
    
    setattr(process, "%sGenTask"%name,
        cms.Task(
            getattr(process, 'Gen%s'%name),
            getattr(process, 'Gen%sTable'%name),
            getattr(process, 'Transfer%sTable'%name),
            getattr(process, 'UnmatchedGen%sTable'%name),
        )
    )
    process.schedule.associate(getattr(process, '%sGenTask'%name))

    if whichEEC in ('res4', 'proj'):
        # add untransfered tables
        setattr(process, 'UntransferedGen%sTable'%name,
            get_table(config, 'Gen%s'%name, whichEEC, 'untransferedGen')
        )
        setattr(process, 'UntransferedReco%sTable'%name,
            get_table(config, 'Gen%s'%name, whichEEC, 'untransferedReco')
        )
        setattr(process, "%sUntransferedTablesTask"%name, cms.Task(
            getattr(process, 'UntransferedGen%sTable'%name),
            getattr(process, 'UntransferedReco%sTable'%name),
        ))
        process.schedule.associate(getattr(process, '%sUntransferedTablesTask'%name))


    return process