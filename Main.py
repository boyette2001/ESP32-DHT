# Complete project details at https://RandomNerdTutorials.com/micropython-mqtt-publish-dht11-dht22-esp32-esp8266/
import ssd1306
from machine import SoftI2C
import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
from machine import Pin
import dht
from time import sleep
esp.osdebug(None)
import gc
gc.collect()

ssid = 'BHNTG1682G7F91'
password = '08a44639'

#assign i2c pin for ESP32
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))

#screen specification
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

mqtt_server = '192.168.0.50'


client_id = ubinascii.hexlify(machine.unique_id())

topic_pub_temp = 'esp/dht/temperatureC'
topic_pub_tempf = 'esp/dht/temperatureF'
topic_pub_hum = 'esp/dht/humidity'

last_message = 0
message_interval = 5

station = network.WLAN(network.STA_IF)

station.active(True)
sleep(3)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
oled.text('WiFi Connected', 0,0)
oled.show()
sleep(2)

sensor = dht.DHT22(Pin(14))
#sensor = dht.DHT11(Pin(14))

def connect_mqtt():
  global client_id, mqtt_server
  client = MQTTClient(client_id, mqtt_server)
  #client = MQTTClient(client_id, mqtt_server, user=your_username, password=your_password)
  client.connect()
  print('Connected to %s MQTT broker' % (mqtt_server))
  oled.fill(0)
  oled.text('MQTT Connected ' ,0,0 )
  oled.text(mqtt_server, 0, 10)
  oled.show()
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

def read_sensor():
  try:
    sensor.measure()
    temp = sensor.temperature()
    # uncomment for Fahrenheit
    tempf = temp * (9/5) + 32.0
    hum = sensor.humidity()
    if (isinstance(temp, float) and isinstance(hum, float)) or (isinstance(temp, int) and isinstance(hum, int)):
      #temp = (b'{0:3.1f},'.format(temp))
      #hum =  (b'{0:3.1f},'.format(hum))
      temp1 = str(temp)
      tempf1 = str(tempf)
      hum1 = str(hum)
      return temp1,tempf1, hum1
    else:
      return('Invalid sensor readings.')
  except OSError as e:
    return('Failed to read sensor.')

try:
  client = connect_mqtt()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    if (time.time() - last_message) > message_interval:
      temp1, tempf1, hum1 = read_sensor()
      print(temp1, 'C')
      print(tempf1, 'F')
      print(hum1, '%')
      oled.fill(0)
      oled.text('Temp %s C' % (temp1),0,0)
      oled.text('Temp %s F' % (tempf1),0,10)
      oled.text('Hum %s  %%' % (hum1),0,20)
      oled.show()      
      client.publish(topic_pub_temp, temp1)
      client.publish(topic_pub_tempf, tempf1)
      client.publish(topic_pub_hum, hum1)
      last_message = time.time()
  except OSError as e:
    restart_and_reconnect()