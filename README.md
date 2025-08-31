# Error Correcting Codes


Python implementations of Reed Solomon, Viterbi (both hard and soft decoding), and Concatenated error correcting codes with a streamlined interface. 

Plus, simulations to evaluate error correction performance under noisy communication conditions.


## Requirements
This code requires Python 3. It has been tested with Python 3.8 in macOs.
Install dependencies by running
```
pip install -r requirements.txt
```

## Usage
### 🚀 Quick start
```
python demo.py
```
This script demonstrates all error correctors and simulation options demonstrated [demo.py](demo.py). 

### Step-by-step walkthrough
1. Initialize an error corrector
    ```
    from error_correctors import ReedSolomon
    rs = ReedSolomon(n, k)

    - n (int): codeword size (a codeword consists of n bytes, k of which are data and n - k of which are parity)
    - k (int): number of data bytes per codeword
    ```

    ```
    from error_correctors import Viterbi
    vit = Viterbi(k, soft = True/False)

    - k (int, 2 or 5): Constraint length of the convolutional code. 
    - soft (bool): Apply soft decoding. Defaults to False (hard decoding)
    ```

    ```
    from error_correctors import ConcatenatedViterbiRS
    concatenated = ConcatenatedViterbiRS(n, k, vit_k, soft = True/False)

    - n (int): Reed Solomon codeword size (a codeword consists of n bytes, k of which are data and n - k of which are parity)
    - k (int): number of data bytes per Reed Solomon code word
    - vit_k (int, 2 or 5): Constraint length of the convolutional code. 
    - soft (bool): Apply soft Viterbi decoding. Defaults to False (hard decoding)
    ```
2. Simulate noisy channel

    Using hard decoding:
    ```
    from simulation import HardDecodingNoisyChannelSimulator

    sim = HardDecodingNoisyChannelSimulator(<error_corrector class>) # initialize
    sim.simulate(bitstring, bit_flip_probability) # run
        - bitstring (string of "0" and "1"): 
        - bit_flip_probability (float): Probability of a bit in the input bitstring being flipped due to channel noise
    ```

    Using soft decoding:    
    ```
    from simulation import SoftDecodingNoisyChannelSimulator

    sim = SoftdDecodingNoisyChannelSimulator(error_corrector) # initialize    
    sim.simulate(bitstring, noise_sigma) # run
        - bitstring (string of "0" and "1"): 
        - noise_sigma (float) standard deviation of Gaussian noise added to the bit probabilities
    ```

## Credits
The error corrector classes are wrappers around [this](https://github.com/DanielBonanno/Convolutional-Encoders-and-Viterbi-Decoder/tree/master) Viterbi implementation and [this](https://pypi.org/project/unireedsolomon/) Reed Solomon implementation.