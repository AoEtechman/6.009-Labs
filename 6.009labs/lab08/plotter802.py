import matplotlib.pyplot as plot
import numpy as np
import datetime
import time
import serial
import signal
import sys
import serial.tools.list_ports

oneReadTimeOut = 1.0
portConnectTimeOutRatio = 5
portTimeOutRatio = 2
defaultXlabel = 'Microseconds'
defaultNumPts = 500

#Automatically finds Teensy USB port, then starts up real time printing. USB
#finder approach thanks to Joe Steinmeyer, real time plotting approach thanks
#to Joshua Hrisko on makersportal

def signal_handler(sig, frame):
    print('Sig Exiting....')
    if ser != []:
        ser.close()
        
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

def streamPlot(x,y,plot1,xLabel="Time In Milliseconds"):
    if plot1 is None and y is not None:  # Create plot, put in x and y
        plot.ion() # Needed to allow real time updates
        fig = plot.figure(figsize=(8,5))
        ax = fig.add_subplot(111)
        plot.ylabel("Measured")
        plot.xlabel(xLabel)
        plot.grid(True);
        plot1, = ax.plot(x,y) # Save plot to do fast y updates.
        plot.show()
            
    # If plot exists, just update the y data
    if y is not None:
        plot1.set_ydata(y)
        # adjust limits if y is a little too large, or way too small.
        limits = plot1.axes.get_ylim()
        lmN = limits[0]
        lmP = limits[1]
        maxy = np.max(y)
        miny = np.min(y)
        stdy = np.std(y)
        if miny<lmN or maxy>lmP :
            plot.ylim([min(miny,lmN)-stdy/2, max(lmP,maxy)+stdy/2])

    plot.show()

    # Nonzero pause is needed to allow GUI events to be processed
    plot.pause(1.0e-4)
    
    # return the plot, so it can be sent back for fast updates
    return plot1

def port_scan():
    ports = list(serial.tools.list_ports.comports())
    port_dict_all = {i: [ports[i], ports[i].vid] for i in range(len(ports))}
    port_dict = []

    for p in port_dict_all:
        if port_dict_all[p][1] == 5824:  # 5824 is Teensy ID.
            port_dict.append(port_dict_all[p][0])

    return port_dict

def connect_serial():
    baud = 1000000
    serialConn = False
 
    s_list = port_scan()

    for s in s_list:  # Loop through Teensy ports until one responds.
            
        ser = serial.Serial(port = s[0], 
                            baudrate=baud,
                            parity=serial.PARITY_NONE, 
                            stopbits=serial.STOPBITS_ONE, 
                            bytesize=serial.EIGHTBITS,
                            timeout=oneReadTimeOut)

        for i in range(portConnectTimeOutRatio):
            try:
                strData = ser.readline()  # First try, got a float?
                if (strData is not None) and (len(strData) > 0):
                    floatData = np.fromstring(strData, dtype=float, sep=',')
                    if len(floatData) > 0:
                        serialConn = True
                        break
            except Exception as e:
                serialConn = False

        if serialConn:
            break
        else:
            ser.close()

    if serialConn: 
        print("Serial Connected!")
        if ser.isOpen():
            print(ser.name + ' is open...')
        return ser
    else:
        print("Timeout: Is the board connected to your laptop and dipswitch 3 set off?")
        return None
    
def keepPlotting(size,unitsLabel,ser):
    xv = np.linspace(0,size,size+1)[0:-1]
    lenxv = len(xv)
    yv = None
    plotxy = None

    while ser is not None:
        for i in range(portTimeOutRatio):
            try:
                strData = ser.readline()  # First try, got a float?
            except Exception as e:
                print("the exception")
                print(e)
                ser.close()
                plot.close()
                return
                
            if len(strData) > 0:
                serialData = True
                break
            else:
                serialData = False
                time.sleep(1.0e-4)

        if serialData == True:
            floatData = np.fromstring(strData, dtype=float, sep=',')
            deltaSize = lenxv - len(floatData)
            
            if yv is None:  # Initial values for y in range of data.
                yv = floatData[-1]*np.ones(lenxv)
                
            if deltaSize > 0:
                yv[0:deltaSize] = yv[lenxv-deltaSize:lenxv];
                yv[deltaSize:lenxv] = floatData;
            else:
                lenfd = len(floatData)
                yv[0:lenxv] = floatData[lenfd-lenxv:lenfd]

            plotxy = streamPlot(xv,yv,plotxy,xLabel=unitsLabel)
        else:
            plotxy = streamPlot(xv,None,plotxy,xLabel=unitsLabel)

    return(plotxy)


if len(sys.argv) > 2:
    unitsLabel = sys.argv[2];
else:
    unitsLabel = defaultXlabel
    
if len(sys.argv) > 1:
    numPoints = int(sys.argv[1]);
else:
    numPoints = defaultNumPts

while True:

    ser = connect_serial()

    if ser is None:
        time.sleep(1)
    else:
        keepPlotting(numPoints,unitsLabel,ser)
        input("press enter to restart")
        sys.stdout.write("Restarting")
        sys.stdout.flush()
        for i in range(5):
            time.sleep(0.1)
            sys.stdout.write(".")
            sys.stdout.flush()
        print("restarting now.")
    
sys.exit(0)


    