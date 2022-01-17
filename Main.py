import time
from umqttsimple import MQTTClient
import ubinascii
import micropython
import esp
import SSD1306
from machine import Pin
from time import sleep
import dht 
import network
from machine import I2C
import machine
import gc
gc.collect()

#setup I2c
i2c = I2C(sda=Pin(21), scl=Pin(22))

#setup screen
display = SSD1306.SSD1306_I2C(128, 64, i2c)

ssid = 'BHNTG1682G7F91'
password = '08a44639'
mqtt_server = '8d9da53f95d74b49a6f32ef6171fdb82.s1.eu.hivemq.cloud'
mqtt_port = 8883
mqtt_user = 'nate2010'
mqtt_password = 'Ar69444!'

client_id = ubinascii.hexlify(machine.unique_id())

#setup topics
topic_pub_temp = b'esp/dht/temperature'
topic_pub_hum = b'esp/dht/humidity'

#message timing
last_message = 0
message_interval = 5

#wifi connection
station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
display.fill(0)
display.text('WiFi connected', 0, 0, 1)
display.show()


sensor = dht.DHT22(Pin(14))
#sensor = dht.DHT11(Pin(14))

def connect_mqtt():
  global client_id, mqtt_server
  client = MQTTClient(client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_password)
  #client = MQTTClient(client_id, mqtt_server, user='nate2010', password='Ar69444!')
  client.connect()
  print('Connected to %s MQTT broker' % (mqtt_server))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_mqtt()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    if (time.time() - last_message) > message_interval:
    #sleep(1)
      sensor.measure()
      temp = sensor.temperature()
      hum = sensor.humidity()
      temp_f = temp * (9/5) + 32.0
      print('Temperature: %3.1f C' %temp)
      print('Temperature: %3.1f F' %temp_f)
      print('Humidity: %3.1f %%' %hum)
      display.fill(0)
      display.text('Temp: %3.1f C'%temp,0,0,1)
      display.text('Temp: %3.1f F'%temp_f,0,10,1)
      display.text('Humidity: %3.1f %%'%hum,0,20,1)
      display.show()
      client.publish(topic_pub_temp, temp)
      client.publish(topic_pub_hum, hum)
      last_message = time.time()
    
  except OSError as e:
    print('Failed to read sensor.')