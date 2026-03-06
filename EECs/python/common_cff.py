from SRothman.EECs.EECProjProducer_cfi import EECProjVectorProducer, EECProjUnbinnedProducer, EECProjArrayProducer
from SRothman.EECs.EECProjMatchedProducer_cfi import EECProjMatchedVectorProducer, EECProjMatchedUnbinnedProducer, EECProjMatchedArrayProducer
from SRothman.EECs.EECProjTransferProducer_cfi import EECProjTransferVectorProducer, EECProjTransferUnbinnedProducer, EECProjTransferArrayProducer
from SRothman.EECs.EECProjTableProducer_cfi import EECProjVectorTableProducer, EECProjUnbinnedTableProducer, EECProjArrayTableProducer
from SRothman.EECs.EECProjTransferTableProducer_cfi import EECProjTransferVectorTableProducer, EECProjTransferUnbinnedTableProducer, EECProjTransferArrayTableProducer
from SRothman.EECs.projcalculator_cfi import get_proj_calculator, get_proj_transfer_calculator

from SRothman.EECs.EECRes3Producer_cfi import EECRes3VectorProducer, EECRes3UnbinnedProducer, EECRes3ArrayProducer
from SRothman.EECs.EECRes3MatchedProducer_cfi import EECRes3MatchedVectorProducer, EECRes3MatchedUnbinnedProducer, EECRes3MatchedArrayProducer
from SRothman.EECs.EECRes3TransferProducer_cfi import EECRes3TransferVectorProducer, EECRes3TransferUnbinnedProducer, EECRes3TransferArrayProducer
from SRothman.EECs.EECRes3TableProducer_cfi import EECRes3VectorTableProducer, EECRes3UnbinnedTableProducer, EECRes3ArrayTableProducer
from SRothman.EECs.EECRes3TransferTableProducer_cfi import EECRes3TransferVectorTableProducer, EECRes3TransferUnbinnedTableProducer, EECRes3TransferArrayTableProducer
from SRothman.EECs.res3calculator_cfi import get_res3_calculator, get_res3_transfer_calculator

from SRothman.EECs.EECRes4Producer_cfi import EECRes4VectorProducer, EECRes4UnbinnedProducer, EECRes4ArrayProducer
from SRothman.EECs.EECRes4MatchedProducer_cfi import EECRes4MatchedVectorProducer, EECRes4MatchedUnbinnedProducer, EECRes4MatchedArrayProducer
from SRothman.EECs.EECRes4TransferProducer_cfi import EECRes4TransferVectorProducer, EECRes4TransferUnbinnedProducer, EECRes4TransferArrayProducer
from SRothman.EECs.EECRes4TableProducer_cfi import EECRes4VectorTableProducer, EECRes4UnbinnedTableProducer, EECRes4ArrayTableProducer
from SRothman.EECs.EECRes4TransferTableProducer_cfi import EECRes4TransferVectorTableProducer, EECRes4TransferUnbinnedTableProducer, EECRes4TransferArrayTableProducer
from SRothman.EECs.res4calculator_cfi import get_res4_calculator, get_res4_transfer_calculator

producers = {
    'proj' : {
        'Vector' : EECProjVectorProducer,
        'Unbinned' : EECProjUnbinnedProducer,
        'Array' : EECProjArrayProducer,
    },
    'res3' : {
        'Vector' : EECRes3VectorProducer,
        'Unbinned' : EECRes3UnbinnedProducer,
        'Array' : EECRes3ArrayProducer,
    },
    'res4' : {
        'Vector' : EECRes4VectorProducer,
        'Unbinned' : EECRes4UnbinnedProducer,
        'Array' : EECRes4ArrayProducer,
    }
}
matchedproducers = {
    'proj' : {
        'Vector' : EECProjMatchedVectorProducer,
        'Unbinned' : EECProjMatchedUnbinnedProducer,
        'Array' : EECProjMatchedArrayProducer,
    },
    'res3' : {
        'Vector' : EECRes3MatchedVectorProducer,
        'Unbinned' : EECRes3MatchedUnbinnedProducer,
        'Array' : EECRes3MatchedArrayProducer,
    },
    'res4' : {
        'Vector' : EECRes4MatchedVectorProducer,
        'Unbinned' : EECRes4MatchedUnbinnedProducer,
        'Array' : EECRes4MatchedArrayProducer,
    }
}
transferproducers = {
    'proj' : {
        'Vector' : EECProjTransferVectorProducer,
        'Unbinned' : EECProjTransferUnbinnedProducer,
        'Array' : EECProjTransferArrayProducer,
    },
    'res3' : {
        'Vector' : EECRes3TransferVectorProducer,
        'Unbinned' : EECRes3TransferUnbinnedProducer,
        'Array' : EECRes3TransferArrayProducer,
    },
    'res4' : {
        'Vector' : EECRes4TransferVectorProducer,
        'Unbinned' : EECRes4TransferUnbinnedProducer,
        'Array' : EECRes4TransferArrayProducer,
    }
}
tableproducers = {
    'proj' : {
        'Vector' : EECProjVectorTableProducer,
        'Unbinned' : EECProjUnbinnedTableProducer,
        'Array' : EECProjArrayTableProducer,
    },
    'res3' : {
        'Vector' : EECRes3VectorTableProducer,
        'Unbinned' : EECRes3UnbinnedTableProducer,
        'Array' : EECRes3ArrayTableProducer,    
    },
    'res4' : {
        'Vector' : EECRes4VectorTableProducer,
        'Unbinned' : EECRes4UnbinnedTableProducer,
        'Array' : EECRes4ArrayTableProducer,
    }
}
transfertableproducers = {
    'proj' : {
        'Vector' : EECProjTransferVectorTableProducer,
        'Unbinned' : EECProjTransferUnbinnedTableProducer,
        'Array' : EECProjTransferArrayTableProducer,
    },
    'res3' : {
        'Vector' : EECRes3TransferVectorTableProducer,
        'Unbinned' : EECRes3TransferUnbinnedTableProducer,
        'Array' : EECRes3TransferArrayTableProducer,
    },
    'res4' : {
        'Vector' : EECRes4TransferVectorTableProducer,  
        'Unbinned' : EECRes4TransferUnbinnedTableProducer,
        'Array' : EECRes4TransferArrayTableProducer,
    }
}
calculator_factories = {
    'proj' : get_proj_calculator,
    'res3' : get_res3_calculator,
    'res4' : get_res4_calculator,
}
transfercalculator_factories = {
    'proj' : get_proj_transfer_calculator,
    'res3' : get_res3_transfer_calculator,
    'res4' : get_res4_transfer_calculator,
}

def get_producer(config, jets, whichEEC, genreco):
    producer = producers[whichEEC][config['resultType']]
    factory = calculator_factories[whichEEC]

    return producer.clone(
        jets = jets,
        flags = [jets + flag for flag in config['flags']],
        calculator = factory(config, genreco),
    )

def get_matched_producer(config, jets, matches, whichEEC, genreco):
    producer = matchedproducers[whichEEC][config['resultType']]
    factory = calculator_factories[whichEEC]
        
    return producer.clone(
        jets = jets,
        matches = matches,
        flags = [jets + flag for flag in config['flags']],
        calculator = factory(config, genreco),
    )

def get_transfer_producer(config, genjets, recojets, matches, whichEEC):
    producer = transferproducers[whichEEC][config['resultType']]    
    factory = transfercalculator_factories[whichEEC]

    return producer.clone(
        genJets = genjets,
        recoJets = recojets,
        matches = matches,
        flags = [recojets + flag for flag in config['flags']],
        calculator = factory(config),
    )

def get_table(config, name, whichEEC, what):
    tableProducer = tableproducers[whichEEC][config['resultType']]

    capswhat = what[0].upper() + what[1:]

    if name.startswith('Gen'):
        tablename = '%s%s'%(capswhat, name[3:])
    else:
        tablename = '%s%s'%(capswhat, name)

    if 'maxOrder' in config:
        tableProducer.maxOrder = config['maxOrder']

    return tableProducer.clone(
        EECs = "%s:%s"%(name, what),
        name = tablename
    )

def get_transfer_table(config, name, whichEEC):
    tableProducer = transfertableproducers[whichEEC][config['resultType']]

    if 'maxOrder' in config:
        tableProducer.maxOrder = config['maxOrder']

    return tableProducer.clone(
        EECTransfer = "%s:transfer"%name,
        name = "%sTransfer"%name,
    )