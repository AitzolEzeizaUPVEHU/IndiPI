from flask import Flask, render_template, request, jsonify
from gpiozero import LED, Button
from PMODKYPDTest import PMODKeypad, disable_spi
import Adafruit_ADS1x15
import time


app = Flask(__name__)

adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)
GAIN = 1
VOLTAGE_RANGE = 4.096
RESOLUTION = VOLTAGE_RANGE / 32768

disable_spi() # Call this function to disable SPI
time.sleep(1)

cols = [11, 9, 10, 8]
rows = [18, 20, 21, 19]
keypad = PMODKeypad(rows, cols)

# Define GPIO pins
output_pins = {
    12: LED(12),
    13: LED(13),
    24: LED(24),
    17: LED(17),
    27: LED(27), 
    22: LED(22),
    5: LED(5),
}

input_pins = {
    14: Button(14),
    15: Button(15)
}


def get_pressed_button():
    key = keypad.get_key()
    if key:
        if key == 'A':
            return 10
        elif key == 'B':
            return 11
        elif key == 'C':
            return 12
        elif key == 'D':
            return 13
        elif key == 'E':
            return 14
        elif key == 'F':
            return 15
        elif key == '0':
            return 16
        else:
            return int(key)
    else:  
        return 0


def get_analog_values():
    values = [0]*4
    for i in range(4):
        # Read the specified ADC channel using the previously set gain value.
        raw_value = adc.read_adc(i, gain=GAIN)
        # Convert raw ADC value to voltage.
        values[i] = raw_value * RESOLUTION
    return {
        "analog0": values[0],  
        "analog1": values[1],  
        "analog2": values[2],  
        "analog3": values[3],
    }

@app.route('/')
def index():
    # Get the state of the input pins
    input_status = {pin: input_pins[pin].is_pressed for pin in input_pins}
    return render_template('index.html', input_status=input_status)

@app.route('/toggle/<int:pin>', methods=['POST'])
def toggle(pin):
    if pin in output_pins:
        output_pins[pin].toggle()
        return jsonify({'status': 'success', 'pin': pin, 'state': output_pins[pin].is_lit})
    return jsonify({'status': 'error', 'message': 'Invalid pin'}), 400

@app.route('/states/<int:pin>', methods=['GET'])
def states(pin):
    if pin in input_pins:
        return jsonify({'status': 'success', 'pin': pin, 'state': "true" if not(input_pins[pin].is_pressed) else "false"}), 200
    return jsonify({'status': 'error', 'message': 'Invalid pin'}), 400

@app.route('/matrix_states', methods=['GET'])
def matrix_states():
    # Initialize the matrix state with all buttons as "Released"
    matrix_state = {f'btn{i}': "Released" for i in range(1, 17)}
    # Get the number of the pressed button (1-16), or 0 if none are pressed
    pressed_button = get_pressed_button()
    # If a button is pressed (not zero), update its status to "Pressed"
    if pressed_button != 0:
        matrix_state[f'btn{pressed_button}'] = "Pressed"    
    # Return the matrix state as JSON
    return jsonify(matrix_state)

@app.route('/analog_values', methods=['GET'])
def analog_values():
    values = get_analog_values()
    return jsonify(values)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)