from error_correctors import *
from simulation import *

# initialize one error corrector of each type
rs = ReedSolomon(5, 3)
soft_viterbi = Viterbi(5, soft = True)
hard_viterbi = Viterbi(5, soft = False)
hard_concatenated = ConcatenatedViterbiRS(5, 5, 3, soft = False)
soft_concatenated = ConcatenatedViterbiRS(5, 5, 3, soft = True)

# run simulation of performance on noisy channel for each
# for the hard decoders, the noise is specified in terms of a bit flip probability
reed_solomon_simulator = HardDecodingNoisyChannelSimulator(rs)
reed_solomon_simulator.simulate("1101001010110100101010101010101010101010101011", 0.25)

hard_viterbi_simulator = HardDecodingNoisyChannelSimulator(hard_viterbi)
hard_viterbi_simulator.simulate("1101001010110100101010101010101010101010101011", 0.25)

hard_concatenated_viterbi_simulator = HardDecodingNoisyChannelSimulator(hard_concatenated)
hard_concatenated_viterbi_simulator.simulate("1101001010110100101010101010101010101010101011", 0.25)

# for soft decoders, the noise is specified in terms of standard deviation of Gaussian noise added to 
# the bit probabilities, i.e., each bit originally is just a 0 or 1, but the received value is a float
# equal to the bit value + random value sampled from a Gaussian distribution
soft_viterbi_simulator = SoftDecodingNoisyChannelSimulator(soft_viterbi)
soft_viterbi_simulator.simulate("1101001010110100101010101010101010101010101011", 0.5)

concatenated_soft_viterbi_simulator = SoftDecodingNoisyChannelSimulator(soft_concatenated)
concatenated_soft_viterbi_simulator.simulate("1101001010110100101010101010101010101010101011", 0.5)

