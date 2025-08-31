"""
Simulation of noisy channel communication with error correction
"""
import random
import numpy as np
from error_correctors import Viterbi, ConcatenatedViterbiRS, ReedSolomon

class HardDecodingNoisyChannelSimulator(object):
    def __init__(self, error_corrector):
        """
        Initialize simulator with error corrector of choice: 
        Reed Solomon OR Viterbi/ConcatenatedViterbiRS class with hard decoding set
        """
        assert isinstance(error_corrector, (ReedSolomon, Viterbi, ConcatenatedViterbiRS)), \
            "Invalid error corrector type. Must be ReedSolomon, Viterbi, or ConcatenatedViterbiRS."
        if isinstance(error_corrector, (Viterbi, ConcatenatedViterbiRS)):
            assert not error_corrector.soft, "Error corrector must be in hard decoding mode."
        self.error_corrector = error_corrector

    def noise_bitstring(self, encoded_bitstring, flip_probability):
        """
        Add noise to an encoded bitstring by flipping bits with probability flip_probability, for testing purposes.

        Args:
            encoded_payload (str): str containing only 0s and 1s, where each 0 and 1 is treated as an actual binary 1/0 value, not
                                   a char "1" or "0"
            flip_probability (float): probability of flipping each bit in the encoded_payload
        
        Returns:
            noised_payload (str): str containing only 0s and 1s, where each 0 and 1 is treated as an actual binary 1/0 value, not
        """
        num_bit_flips = 0
        noised_payload = ""
        for i in encoded_bitstring:
            if random.randint(0, 100) < flip_probability*100:
                num_bit_flips += 1
                if i == "1":
                    noised_payload += "0"
                else:
                    noised_payload += "1"
            else:
                noised_payload += i
        return noised_payload, num_bit_flips


    def simulate(self, message_bitstring, error_probability):
        """
        Simulate sending an coded message bitstring through a noisy channel that flips bits
        and applying hard decoding on the corrupted bitsring to correct errors.
        
        Args:
            message_bitstring (str): str containing only 0s and 1s, where each 0 and 1 is treated as an actual binary 1/0 value, not
                                        a char "1" or "0"
            error_probability (float): probability of flipping each bit in the encoded message during transmission
        """
        encoded_payload = self.error_corrector.encode(message_bitstring)
        noised_payload, num_bit_flips = self.noise_bitstring(encoded_payload, error_probability)
        decoded_payload, _ = self.error_corrector.decode(noised_payload)
        err = sum(c1!=c2 for c1,c2 in zip(message_bitstring, decoded_payload))
        print(f"----- HARD DECODING NOISY CHANNEL SIMULATOR -----")
        print(f"{self.error_corrector.name}")
        print(f"Input bitstring:     {message_bitstring}")
        print(f"Encoded bitstring:   {encoded_payload}")
        print(f"Noised bitstring:    {noised_payload}")
        print(f"Decoded bitstring: {decoded_payload}")
        print(f"{num_bit_flips} bits flipped during noise addition.")
        print(f"Total errors: {err} bits")
        print("--------------------------------------------------")

class SoftDecodingNoisyChannelSimulator(object):
    def __init__(self, error_corrector):
        """
        Initialize simulator with error corrector of choice: 
        Reed Solomon OR Viterbi/ConcatenatedViterbiRS class with soft decoding set
        """
        assert isinstance(error_corrector, (ReedSolomon, Viterbi, ConcatenatedViterbiRS)), \
            "Invalid error corrector type. Must be ReedSolomon, Viterbi, or ConcatenatedViterbiRS."
        assert error_corrector.soft, "Error corrector must be in soft decoding mode."
        self.error_corrector = error_corrector

    def noise_bitstring(self, encoded_bitstring, noise_sigma):
        """
        Add Gaussian noise to an encoded bitstring.

        Args:
            encoded_bitstring (str): str containing only 0s and 1s, where each 0 and 1 is treated as an actual binary 1/0 value, not
                                   a char "1" or "0"
            noise_sigma (float): standard deviation of the Gaussian noise to add

        Returns:
            noised_payload (list): list of floats representing the noised bitstring
        """
        noised_payload = []
        for i in encoded_bitstring:
            if i == "1":
                mu = -1
            else:
                mu = 1
            soft_value = np.random.normal(mu, noise_sigma)
            noised_payload.append(soft_value)
        return noised_payload

    def simulate(self, message_bitstring, noise_sigma):
        """
        Simulate sending an coded message bitstring through a noisy channel that adds Gaussian noise
        with standard deviation noise_sigma to the symbol values.
        Then apply soft decoding on the corrupted bitsring to correct errors.

        Args:
            message_bitstring (str): str containing only 0s and 1s, where each 0 and 1 is treated as an actual binary 1/0 value, not
                                        a char "1" or "0"
            noise_sigma (float): standard deviation of Gaussian noise added to
                                the bit probabilities, i.e., each bit originally is just a 0 or 1, but the received value is a float
                                equal to the bit value + random value sampled from a Gaussian distribution
        """
        encoded_payload = self.error_corrector.encode(message_bitstring)
        noised_payload = self.noise_bitstring(encoded_payload, noise_sigma)
        decoded_payload, _ = self.error_corrector.decode(noised_payload)
        err = sum(c1!=c2 for c1,c2 in zip(message_bitstring, decoded_payload))
        print(f"----- SOFT DECODING NOISY CHANNEL SIMULATOR -----")
        print(f"{self.error_corrector.name}")
        print(f"Input bitstring:     {message_bitstring}")
        print(f"Encoded bitstring:   {encoded_payload}")
        print(f"Noised bit probabilities:    {noised_payload}")
        print(f"Decoded bitstring: {decoded_payload}")
        print(f"Total errors: {err} bits")
        print("--------------------------------------------------")

