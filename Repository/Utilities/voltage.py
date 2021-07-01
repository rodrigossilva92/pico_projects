from machine import ADC

adcResolution = const(65536)

def getInputVoltage():
    Vbus = ADC(29).read_u16()/adcResolution*3.3
    Vsys = Vbus*3    
    return Vsys

# print(getInputVoltage())