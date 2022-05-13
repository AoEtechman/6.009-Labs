# No Imports Allowed!


def backwards(sound):
    """
    this function takes in a mono sound file dictionary input and returns a new sound
    dictionary with the same rate and a samples dictionary where the samples
    have been reversed from the original sound's samples 
    """
   
    #initialize rate and list of samples from input sound dict
    rate  = sound["rate"]
    samples_list = sound["samples"]
    
    #slice samples list into a new list in reversed order
    new_lst = samples_list[-1:-len(samples_list)-1:-1]
    
    #return dict with backwards samples
    return { "rate": rate, 
    "samples": new_lst
    }
    

def mix(sound1, sound2, p):
    
    """
    This function takes in two mono sound dictionary inputs, as well as a mixing parameter input,
    and returns a sound dictionary with samples that are a mix of the two sounds with the same 
    sampling rate. The sampling implimentation scales the first sound's sample lists by p and then the second
    sound by 1-p. The two sounds sample lists are then added together.
    """
    #initialize the rates and samples for both sounds
    rate1 = sound1["rate"]
    rate2 = sound2["rate"]
    sample_lst1 = sound1["samples"]
    sample_lst2 = sound2["samples"]
    
    #if rates of the two sounds are not equal, cannot mix, return none
    if rate2 != rate1:
        return None
    
    # initialize new list and a combined list
    new_list1 = []
    new_list2 = []
    combined_list = []
    
    # get the min length of the two sounds
    min_len = min(len(sample_lst1),len(sample_lst2))
    
    # iterate through both sample list and add new scaled sample values to the new lists
    for i in range(min_len):
        new_list1.append(sample_lst1[i]*p)
        new_list2.append(sample_lst2[i]*(1-p))   
    
    #add the two lists into a combined list
    for i in range(min_len):
        combined_list.append(new_list1[i]+ new_list2[i]) 
    
    #return sound dict with mixed samples
    return {"rate": rate1,
    "samples": combined_list}


        

    


def convolve(sound, kernel):
    
    """
    takes a mono sound file dictionary input and kernel input which is a list of values,
    and returns a sound file dictionary with the same rate and a sample list that is
    a result of the convolve implimentation. The convolve implimentation iterates through values from
    the kernel, and shifts samples in the sample list by the kernel value's index, and then scales the
    samples by the kernel value.
    """
    # initialize length of kernel, sample list, an empty scaled list, and an empty added_samples list
    kern_length = len(kernel) - 1
    lists_scaled_samples = []
    added_samples_list  = []
    samples_list = sound["samples"]
    
    # append empty added list with desired number of zeros - length of convolved sound, makes it easy to add lists later on
    for i in range(len(samples_list)+kern_length):
        added_samples_list.append(0)

    # iterate through values in kernel
    for n in range(len(kernel)):
        
        scale = kernel[n]    #set scale
        conv_samples = []    #create new empty list of samples scaled by this specific scale
        
        # if scale is not zero, append conv samples list with sample values scaled by the scale
        if scale != 0:       
            for sample in samples_list:
                conv_samples.append(scale*sample)
            else:
                for i in range(n):
                    conv_samples.insert(0,0)  #shift con_samples list by i
                for i in range(kern_length - n):
                    conv_samples.append(0)  #add zeros to end of list to ensure conv_samples is length of convolved sound
            lists_scaled_samples.append(conv_samples) # append a list with each convolved samples list
    
    # add the values from all of the convolved sample lists together
    for lst in lists_scaled_samples:
        for i in range(len(lst)):
            added_samples_list[i] += lst[i]
    return {"rate": sound["rate"], "samples": added_samples_list} # return dict with convolved samples

            


def echo(sound, num_echoes, delay, scale):
    
    """
    takes in a mono sound file dicionary, a integer representing the num of echos,
    an int representing the length of the delay, and an interger representing
    the scale factor. The function returns a sound file dictionary with the same
    rate and a list of samples that are a result of the echo implimentation. The echo
    implimentation takes the samples, delays them by a desired number of samples, and 
    scales down the sample values with each echo.
    """
    # initialize sample delay, samples list, empty list of all of offset lists, max number of samples that an echo
    # can be offset by, and an empty list for adding the lists togther
    sample_delay = round(delay*sound["rate"])
    samples_list = sound["samples"]
    list_of_offsets = []
    length = sample_delay*num_echoes
    added_list = []
    
    # append added list with zeros corresponding to the length of our desired echo samples list
    for k in range(length + len(samples_list)):
        added_list.append(0)
    new_samples_list = samples_list [::] # slice list into new list so we don't edit the input

    #iterate through each echo
    for i in range(num_echoes):
        offset_list = []  # initialize empty offet list for each echo
        for j in range(sample_delay*(i+1)):  #add zeros to begging of list to represent the echo offset
            offset_list.append(0)
        for sample in samples_list:  # add scaled samples to offset list
            offset_list.append(sample*(scale**(i+1)))
        for i in range(length-(sample_delay*(i+1))):  # append zeros to end of offset list to ensure offset list 
            offset_list.append(0)                     # is as long oas the desired echo samples list length
        list_of_offsets.append(offset_list)           # append list of echo lists with current echo offset list
    
    # add zeros to end of samples list to ensure sampled list is the length of desired echo list
    for i in range(sample_delay*num_echoes):
        new_samples_list.append(0)
    
    # add all of the offset lists and the original list together to get desired echo list
    for lst in list_of_offsets:
        for i in range(len(lst)):
            added_list[i] += lst[i]
    for i in range(len(samples_list)):
        added_list[i]+= new_samples_list[i]
    
    return {"rate": sound["rate"], "samples": added_list} # return dict with echo list




def pan(sound):
    
    """
    this function takes in a stereo sound file dictionary input, and returns 
    a sound file dictionary with the same rate and a samples list that 
    has is a result of the pan implimentation. The pan inplimentation applies
    a function to the right and left samples in order to move audio from
    the left stereo to the right steroe
    """
    
    # intialize right and left samples
    right_sample = sound["right"]
    left_sample = sound["left"]
    copy_left_sample = left_sample[::]
    copy_right_sample = right_sample[::]
    
    #for length of sound, iterate through values in left and right
    N = len(left_sample)
    for i in range(N):
        if i == 0:     # if on first value, conduct different tasks for left and right samples
            copy_right_sample[i] = 0
            copy_left_sample[i] = copy_left_sample[i]
        elif i == N-1:  # if on last value, conduct diff tasks for left and right samples
            copy_right_sample[i] = copy_right_sample[i]
            copy_left_sample[i] = 0
        else:  # else carry on with pan function as usual, updating sample lists with the new pan value
            copy_right_sample[i] = copy_right_sample[i] * (i/(N-1))
            copy_left_sample[i] = copy_left_sample[i] * (1-(i/(N-1)))
    return {"rate": sound["rate"], "left": copy_left_sample, "right": copy_right_sample} # return dict with pan value
            
                


def remove_vocals(sound):
   
    """
    this function takes in a stereo sound file dictionary input
    and returns a sound file dictionary with the same rate
    and a sample list where the samples represent the implimentation 
    of removing vocals which is subtracting the right sample list from
    the left one.
    """
    # intialize left and right samples
    right_sample = sound["right"]
    left_sample = sound["left"]
    copy_left_sample = left_sample[::]
    copy_right_sample = right_sample[::]
    
    # create empty kareoke list
    kareoke_version = []
    
    # iterate through each value in samples and subtract left from right
    for i in range(len(left_sample)):
        kareoke_version.append(copy_left_sample[i]-copy_right_sample[i]) #update kareoke list with subtracted value
    
    return {"rate": sound["rate"], "samples": kareoke_version} # return dict with vocal removed samples


def bass_boost_kernel(N, scale=0):
    """
    Construct a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ N

    Then we scale that piece up and add a copy of the original signal back in.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    kernel = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    for i in range(N):
        kernel = convolve(kernel, base['samples'])
    kernel = kernel['samples']

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel)//2] += 1

    return kernel


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct

def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {'rate': sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left.append(struct.unpack('<h', frame[:2])[0])
                right.append(struct.unpack('<h', frame[2:])[0])
            else:
                datum = struct.unpack('<h', frame)[0]
                left.append(datum)
                right.append(datum)

        out['left'] = [i/(2**15) for i in left]
        out['right'] = [i/(2**15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left = struct.unpack('<h', frame[:2])[0]
                right = struct.unpack('<h', frame[2:])[0]
                samples.append((left + right)/2)
            else:
                datum = struct.unpack('<h', frame)[0]
                samples.append(datum)

        out['samples'] = [i/(2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')

    if 'samples' in sound:
        # mono file
        outfile.setparams((1, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = [int(max(-1, min(1, v)) * (2**15-1)) for v in sound['samples']]
    else:
        # stereo
        outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = []
        for l, r in zip(sound['left'], sound['right']):
            l = int(max(-1, min(1, l)) * (2**15-1))
            r = int(max(-1, min(1, r)) * (2**15-1))
            out.append(l)
            out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    
    #mystery = load_wav('sounds/mystery.wav')
    #write_wav(backwards(mystery), 'mystery_reversed.wav')
    # synth = load_wav("sounds/synth.wav")
    # water = load_wav("sounds/water.wav")
    # write_wav(mix(synth,water,.2), "water_synth_mixed.wav")
    # ice_and_chilli = load_wav("sounds/ice_and_chilli.wav")
    # write_wav(convolve(ice_and_chilli, bass_boost_kernel(1000,1.5)), "ice_and_chilli.wav")
    # chord = load_wav("sounds/chord.wav")
    # write_wav(echo(chord, 5, .3, .6), "chord_echo.wav")
    # car = load_wav("sounds/car.wav", True)
    # write_wav(pan(car), "pan_car.wav")
    # l_m = load_wav("sounds/lookout_mountain.wav", True)      
    # write_wav(remove_vocals(l_m),"l_m.wav")
    
