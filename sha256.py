import math

def sha256(input_string):

    #convert string to binary
    bin_str = string2binary(input_string)

    #get length of original string
    bin_len = len(bin_str)

    #append 1 to the end of the binary string
    bin_str += "1"

    #pad with zeros until length is a multiple of 512 - 64
    bin_str = pad_to_multiple(bin_str)

    #convert original length of string to binary
    bin_len = int_to_binary(bin_len)

    #left pad binary length to 64 bits
    bin_len = ("0" * (64 - len(bin_len))) + bin_len

    #append length bits to binary string
    bin_str += bin_len

    #initialize hash values
    #these are the first 32 bits of the fractional parts of the 
    #square roots of the first 8 primes: 2, 3, 5, 7, 11, 13, 17, 19
    hash_values = [
        '01101010000010011110011001100111', 
        '10111011011001111010111010000101', 
        '00111100011011101111001101110010', 
        '10100101010011111111010100111010', 
        '01010001000011100101001001111111', 
        '10011011000001010110100010001100', 
        '00011111100000111101100110101011', 
        '01011011111000001100110100011001'
        ]

    #initialize round constants
    #these the first 32 bits of the fractional parts of the cube roots of 
    #the first 64 primes (2 – 311)
    round_constants = [
        '01000010100010100010111110011000', '01110001001101110100010010010001', '10110101110000001111101111001111', 
        '11101001101101011101101110100101', '00111001010101101100001001011011', '01011001111100010001000111110001', 
        '10010010001111111000001010100100', '10101011000111000101111011010101', '11011000000001111010101010011000', 
        '00010010100000110101101100000001', '00100100001100011000010110111110', '01010101000011000111110111000011', 
        '01110010101111100101110101110100', '10000000110111101011000111111110', '10011011110111000000011010100111', 
        '11000001100110111111000101110100', '11100100100110110110100111000001', '11101111101111100100011110000110', 
        '00001111110000011001110111000110', '00100100000011001010000111001100', '00101101111010010010110001101111', 
        '01001010011101001000010010101010', '01011100101100001010100111011100', '01110110111110011000100011011010', 
        '10011000001111100101000101010010', '10101000001100011100011001101101', '10110000000000110010011111001000', 
        '10111111010110010111111111000111', '11000110111000000000101111110011', '11010101101001111001000101000111', 
        '00000110110010100110001101010001', '00010100001010010010100101100111', '00100111101101110000101010000101', 
        '00101110000110110010000100111000', '01001101001011000110110111111100', '01010011001110000000110100010011', 
        '01100101000010100111001101010100', '01110110011010100000101010111011', '10000001110000101100100100101110', 
        '10010010011100100010110010000101', '10100010101111111110100010100001', '10101000000110100110011001001011', 
        '11000010010010111000101101110000', '11000111011011000101000110100011', '11010001100100101110100000011001', 
        '11010110100110010000011000100100', '11110100000011100011010110000101', '00010000011010101010000001110000', 
        '00011001101001001100000100010110', '00011110001101110110110000001000', '00100111010010000111011101001100', 
        '00110100101100001011110010110101', '00111001000111000000110010110011', '01001110110110001010101001001010', 
        '01011011100111001100101001001111', '01101000001011100110111111110011', '01110100100011111000001011101110', 
        '01111000101001010110001101101111', '10000100110010000111100000010100', '10001100110001110000001000001000', 
        '10010000101111101111111111111010', '10100100010100000110110011101011', '10111110111110011010001111110111', 
        '11000110011100010111100011110010'
        ]

    #parse the binary string into an 32 bit chunks
    words = []
    for i in range(1,math.ceil(len(bin_str)/32) + 1):
        words.append(bin_str[((i-1)*32):(i*32)])

    #parse the resulting array into 512 bit blocks composed of the 32 bit chunks
    blocks = []
    for i in range(math.ceil(len(words)/16)):
        tmp = []
        for j in range(16):
            tmp.append(words[(i*16) + j])
        blocks.append(tmp)
    
    #do the following for each 512 bit block of data
    for block in blocks:
        #add 48 more 32 bit words (initialized to 0) to the original 16, for a total of 64 words
        for i in range(48):
            block.append("0" * 32)

        #modify all of the newly add 0'ed words to be mutations of the original words
        for i in range(16, 64):

            #rotate/shift the bits from word i-15 
            working_word = block[i - 15]
            s0_rotations = [rightrotate(working_word, 7), rightrotate(working_word, 18), rightshift(working_word, 3)]

            #xor the rotations together
            s0 = xor(xor(s0_rotations[0], s0_rotations[1]), s0_rotations[2])

            #repeat the above for word i-2, with different rotations/shifts
            working_word = block[i - 2]
            s1_rotations = [rightrotate(working_word, 17), rightrotate(working_word, 19), rightshift(working_word, 10)]

            #xor the rotations together
            s1 = xor(xor(s1_rotations[0], s1_rotations[1]), s1_rotations[2])

            #add blocks[i-16] + s0 + blocks[i-7] + s1
            #then trim or pad to 32 bits
            #block[i] = pad_to_size(int_to_binary(int(block[i-16], 2) + int(s0,2) + int(block[i-7],2) + int(s1,2))[-32:], 32)
            block[i] = bin_add([block[i-16], s0, block[i-7], s1])
        
        #begin compression logic
        #initialize variables a, b, c, d, e, f, g, h and set them equal to hash_values[0:7]
        a = hash_values[0]
        b = hash_values[1]
        c = hash_values[2]
        d = hash_values[3]
        e = hash_values[4]
        f = hash_values[5]
        g = hash_values[6]
        h = hash_values[7]

        #do the sha256 compression function by mutating the values of a-h
        for i in range(64):
            #s1 = e rrotated by 6, 11, and 25 then xor'd together
            s1 = xor(xor(rightrotate(e, 6), rightrotate(e, 11)), rightrotate(e, 25))
            
            #ch = (e & f) xor (!e & g)
            ch = xor(bin_and(e, f), bin_and(bin_not(e), g))

            #temp1 = h + S1 + ch + round_constants[i] + block[i]
            temp1 = bin_add([h, s1, ch, round_constants[i], block[i]])

            #s0 = a rrotated by 2, 13, and 22 then xor'd together
            s0 = xor(xor(rightrotate(a,2), rightrotate(a,13)), rightrotate(a,22))

            #maj = (a & b) xor (a & c) xor (b & c)
            maj = xor(xor(bin_and(a, b), bin_and(a, c)), bin_and(b, c))

            #temp2 = s0 + maj
            temp2 = bin_add([s0, maj])

            h = g
            g = f
            f = e
            e = bin_add([d, temp1])
            d = c
            c = b
            b = a
            a = bin_add([temp1, temp2])
        
        #after the compression logic, modify the original hash values by adding the a-h variables back to them
        hash_values[0] = bin_add([hash_values[0], a])
        hash_values[1] = bin_add([hash_values[1], b])
        hash_values[2] = bin_add([hash_values[2], c])
        hash_values[3] = bin_add([hash_values[3], d])
        hash_values[4] = bin_add([hash_values[4], e])
        hash_values[5] = bin_add([hash_values[5], f])
        hash_values[6] = bin_add([hash_values[6], g])
        hash_values[7] = bin_add([hash_values[7], h])

    #finally, append all the hash values together and return
    digest = ""
    for x in hash_values:
        digest += x
    
    return hex(int(digest,2))

#convenience functions 

def string2binary(input_string):
    return ''.join(format(ord(i),'b').zfill(8) for i in input_string)

def pad_to_multiple(input_binary):
    nearest_multi = math.ceil((len(input_binary)) / 512)

    #if the length of the binary string is greater than the nearest multiple of 512 - 64
    #go to the next nearest multiple
    if(len(input_binary) > ((nearest_multi * 512) - 64)):
        nearest_multi += 1

    input_binary += "0" * ((nearest_multi * 512) - 64 - (len(input_binary)))

    return input_binary

def pad_to_size(input_binary, length):
    return ("0" * (length - len(input_binary))) + input_binary

def int_to_binary(input_num):
    return '{0:08b}'.format(input_num)

def rightrotate(bits, amount):
    return bits[-amount:] + bits[:-amount]

def rightshift(bits, amount):
    return ("0" * amount) + bits[:-amount]

def xor(input_1, input_2):
    output = ""
    for x in range(len(input_1)):
        output += str(int(input_1[x] != input_2[x]))
    
    return output

def bin_and(input_1, input_2):
    output = ""
    for x in range(len(input_1)):
        output += str(int(input_1[x] == input_2[x] == "1"))
    
    return output

def bin_not(input_binary):
    output = ""
    for x in input_binary:
        output += str(int(x == "0"))
    
    return output

def bin_add(bin_list):
    output = 0
    for x in bin_list:
        output += int(x, 2)
    
    output = pad_to_size(int_to_binary(output)[-32:], 32)
    return output


to_hash = input("Enter text to hash: ")
print("Hashed text:\n" + sha256(to_hash)[2:])