"""
Various error correcting codes: Reed Solomon, Viterbi, Concatenated Reed Solomon + Viterbi 
"""
import unireedsolomon as rs
import random

from viterbi import bit_encoder_K2, bit_encoder_K5, stream_encoder, Decoder
from bitstring_utils import bitstring_to_ascii, ascii_to_bitstring


class ReedSolomon(object):
    """
    Reed Solomon error correction code
    Wrapper around unireedsolomon library: https://pypi.org/project/unireedsolomon/
    """
    def __init__(self, n, k):
        """
        Args:
            n (int): codeword size (a codeword consists of n bytes, k of which are data and n - k of which are parity)
            k (int): number of data bytes
        """
        self.n = n
        self.k = k
        self.coder = rs.RSCoder(n, k)
        self.name = f"ReedSolomon(n={n}, k={k})"

    def strength(self):
        """
        Returns:
            int: number of symbol errors that can be corrected by this Reed Solomon code
            Based on https://www.cs.cmu.edu/~guyb/realworld/reedsolomon/reed_solomon_codes.html
        """
        return (self.n - self.k)/2 #number of error symbols that can be corrected

    def bitstring_to_codewords(self, bitstring):
        """
        Converts a bitstring into a list of codewords. Each codeword is represented as an ASCII string of length n.
        Args:
            bitstring (str): str containing only 0s and 1s, where each 0 and 1 is treated as an actual binary 1/0 value, not
                             a char "1" or "0"
        Returns:
            list: list of codewords, where each codeword is represented as an ASCII string of length n
        """
        chunk_size = self.n * 8
        codewords = []
        for i in range(0, len(bitstring), chunk_size):
            chunk = bitstring[i:i+chunk_size]
            codeword = bitstring_to_ascii(chunk)
            codewords.append(codeword)
        return codewords

    def codewords_to_bitstring(self, codewords):
        """
        Converts a list of codewords into a bitstring.

        Args:
            codewords (list): list of codewords, where each codeword is represented as an ASCII string of length n
        Returns:
            str: str containing only 0s and 1s, where each 0 and 1 is treated as an actual binary 1/0 value, not
                 a char "1" or "0"
        """
        bitstring = ""
        for c in codewords:
            bitstring += ascii_to_bitstring(c)
        return bitstring

    def encode(self, message_bitstring):
        """
        Code a message bitstring via Reed Solomon encoding.
        Args:
            message_bitstring (str): str containing only 0s and 1s, where each 0 and 1 is treated as an actual binary 1/0 value, not
                                      a char "1" or "0"

        Returns:
            str: the encoded bitstring, containing only 0s and 1s, where each 0 and 1 is treated as an actual binary 1/0 value, not
                 a char "1" or "0"
        """
        #convert message bitstring to ascii for compatibility with the ReedSolomon coder 
        # which expects input in the form of 8-bit symbols 
        message_symbols = bitstring_to_ascii(message_bitstring)

        #split symbols into chunks of size n and obtain codeword for each 
        #if the last chunk has less than n bytes, pad it with 0x00 ASCII character until it is of size n
        codewords = []
        for i in range(0, len(message_symbols), self.k):
            if i + self.k > len(message_symbols):
                num_padding_symbols = self.k - (len(message_symbols) - i)
                chunk = message_symbols[i:]
                for n in range(num_padding_symbols):
                    chunk += chr(0)
            else:
                chunk = message_symbols[i:i+self.k]
            codeword = self.coder.encode(chunk)
            codewords.append(codeword)
        enc_bitstring = self.codewords_to_bitstring(codewords)
        return enc_bitstring

    def decode(self, encoded_bitstring):
        """
        Decode an encoded bitstring via Reed Solomon decoding and return the decoded bitstring.

        Args:
            encoded_bitstring (str): str containing only 0s and 1s, where each 0 and 1 is treated as an actual binary 1/0 value, not
                                      a char "1" or "0"
        
        Returns:
            str: the decoded bitstring, containing only 0s and 1s, where each 0 and 1 is treated as an actual binary 1/0 value, not
                 a char "1" or "0"
        """
        codewords = self.bitstring_to_codewords(encoded_bitstring)
        recovered_bitstring = ""
        correctable = True
        for i, c in enumerate(codewords):
            try:
                recovered_chunk_symbols = self.coder.decode(c, nostrip = True)[0]
            except Exception as e:
                # print(f"Reed Solomon can't corect codeword {i}. {e}. Recovered message will just be uncorrected data portion of codeword.")
                recovered_chunk_symbols = c[:self.k]
                correctable = False
            recovered_chunk_bitstring = ascii_to_bitstring(recovered_chunk_symbols)
            recovered_bitstring += recovered_chunk_bitstring
        return recovered_bitstring, correctable

    def check(self, test_message_bitstring):
        """
        Check the Reed Solomon encoding and decoding process by comparing the original
        message bitstring with the recovered bitstring after encoding and decoding.
        """
        codewords = self.encode(test_message_bitstring)
        recovered_bitstring = self.decode(codewords)
        err = sum(c1!=c2 for c1,c2 in zip(test_message_bitstring, recovered_bitstring))
        print("----- REED SOLOMON CHECK -----")
        print(f"Input bitstring:     {test_message_bitstring}")
        print(f"Recovered bitstring: {recovered_bitstring}")
        print(f"Total errors: {err} bits") 


class Viterbi(object):
    """
    Viterbi error correction code with soft decoding
    Wrapper around implementation at 
    https://github.com/DanielBonanno/Convolutional-Encoders-and-Viterbi-Decoder/tree/master
    """
    def __init__(self, k, soft = False):
        """
        Args:
            k (int): Constraint length of the convolutional code, i.e., length of the shifting register in the encoder. 
                        Currently only k = 2 and k = 5 are supported.
        """
        self.k = k
        self.soft = soft
        if k == 2:
            self.bit_encoder = bit_encoder_K2
        elif k == 5:
            self.bit_encoder = bit_encoder_K5
        self.name = f"Viterbi(constraint length k={k}, soft decoding ={soft})"

    def encode(self, input_bitstring):
        """
        Encode a bitstring via Viterbi encoding and return the encoded bitstring.

        Args:
            input_bitstring (str): str containing only 0s and 1s, where each 0 and 1 is treated as an actual binary 1/0 value, not
                                        a char "1" or "0"
        
        Returns:
            str: the encoded bitstring, containing only 0s and 1s, where each 0 and 1 is treated as an actual binary 1/0 value, not
                    a char "1" or "0"
        """
        input_stream = [int(i) for i in input_bitstring]
        list_output = stream_encoder(self.k, input_stream)
        encoded_bitstring = ""
        for el in list_output:
            encoded_bitstring += str(el[0])
            encoded_bitstring += str(el[1])
        return encoded_bitstring

    def decode(self, input):
        """
        Decode a Viterbi-encoded bitstring using soft decision decoding.

        Args:
            input (list of floats or string): If softdecoding is being used, must be list of floats, 
                                                    where each float representing the probability of a bit being a 1 vs 0.
                                                    Probabilities are in range -1-1, where positive numbers are probabilities of being 0, 
                                                    negative numbers are probabilities of being 1.
                                                    If hard decoding is being used, must be a string of 0s and 1s.

        Returns:
            dec_bitstring (str): the decoded bitstring, containing only 0s and 1s, where each 0 and 1 is treated as an actual binary 1/0 value, not
                                  a char "1" or "0"
            correctable (bool): whether the Viterbi error correction was successful. 
        """
        if self.soft:
            if not isinstance(input, list):
                raise ValueError("Input must be a list of floats if using soft decoding. Current type: {}".format(type(input)))
            if not all(isinstance(i, float) for i in input):
                raise ValueError("All elements in the input list must be floats. Current types: {}".format([type(i) for i in input]))
        else:
            if not isinstance(input, str):
                raise ValueError("Input must be a string of 0s and 1s if using hard decoding.")
        if isinstance(input, str):
            input = [float(i) for i in input]
        input_stream = []
        correctable = True
        if len(input) % 2 != 0 or len(input) < self.k:
            correctable = False
        else:
            for i in range(0, len(input), 2):
                input_stream.append([input[i], input[i + 1]])
            try:
                dec_list = Decoder(self.k, input_stream, not self.soft)
            except:
                correctable = False
        if not correctable:
            print(f"Viterbi decoder failed. Returning {(len(input_stream) - self.k)} 0s")
            dec_bitstring = "0" * (len(input) - self.k)
        else:
            dec_bitstring = ""
            for b in dec_list:
                dec_bitstring += str(b)
        return dec_bitstring, correctable


class ConcatenatedViterbiRS(object):
    """
    Concatenated error correction: first Viterbi, then Reed Solomon on Viterbi-encoded data
    """
    def __init__(self, v_k, n, rs_k, soft = False):
        """
        Initialize a concatenated error correction code with an inner Viterbi 
        encoder and an outer Reed Solomon (RS) encoder

        Args:
            v_k (int): Viterbi encoding k
            n (int): Reed Solomon codeword size (a codeword consists of n bytes, 
                     k of which are data and n - k of which are parity)
            rs_k (int): number of data bytes input to Reed Solomon encoder
        """
        self.soft = soft
        self.viterbi_coder = Viterbi(v_k, soft = soft)
        self.rs_coder = ReedSolomon(n, rs_k)
        self.name = f"ConcatenatedViterbiRS(Viterbi constraint length={v_k}, Reed Solomon n={n}, Reed Solomon k={rs_k}, soft decoding={soft})"

    def encode(self, input_bitstring):
        """
        First do Viterbi encoding on input bitstring, then run Reed-Solomon 
        encoding on the Viterbi-encoded bitstring

        Args:
            input_bitstring (str): the input bitstring to be encoded. 
        
        Returns:
            final_encoded (str): the final encoded bitstring (after both Viterbi and RS encoding)
            rs_encoded (str): the Reed Solomon coded bitstring (i.e., pre-Viterbi encoding, post-RS encoding)

        Note: Here, a bitstring is a string of 0s and 1s, where each 0 and 1 is treated as an actual binary 1/0 value, not a char
              e.g., "100010010010"
        """
        rs_encoded = self.rs_coder.encode(input_bitstring)
        final_encoded = self.viterbi_coder.encode(rs_encoded)
        return final_encoded

    def decode(self, input):
        """
        First do soft Viterbi decoding on input probabilities to recover a Reed-Solomon codeword.
        Then run RS decoding on codeword to obtain final data

        Args:
            input (list of floats or string): If softdecoding is being used, must be list of floats, 
                                                    where each float representing the probability of a bit being a 1 vs 0.
                                                    Probabilities are in range -1-1, where positive numbers are probabilities of being 0, 
                                                    negative numbers are probabilities of being 1.
                                                    If hard decoding is being used, must be a string of 0s and 1s.
        
        Returns:
            decoded_bitstring (str): the decoded bitstring (after both Viterbi and RS decoding)
            pred_rs_encoded (str): the Reed Solomon coded bitstring (i.e., post-Viterbi decoding, pre-RS decoding)
            correctable (bool): whether the error correction was successful, considering any errors encountered Viterbi and/or RS decoding
        
        Note: Here, a bitstring is a string of 0s and 1s, where each 0 and 1 is treated as an actual binary 1/0 value, not a char
              e.g., "100010010010"
        """
        if self.soft:
            if not isinstance(input, list):
                raise ValueError("Input must be a list of floats if using soft decoding. Current type: {}".format(type(input)))
            if not all(isinstance(i, float) for i in input):
                raise ValueError("All elements in the input list must be floats. Current types: {}".format([type(i) for i in input]))
        else:
            if not isinstance(input, str):
                raise ValueError("Input must be a string of 0s and 1s if using hard decoding.")
        pred_rs_encoded, vit_corectable = self.viterbi_coder.decode(input)
        decoded_bitstring, rs_correctable = self.rs_coder.decode(pred_rs_encoded)
        correctable = vit_corectable and rs_correctable
        return decoded_bitstring, correctable

