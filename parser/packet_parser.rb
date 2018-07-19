#!/usr/bin/env ruby

#  1               2                     3                        4   5    6    7   8
# 043E2102010301 1C0CB35CBBD5 15 0201 04 11FF5900 0100 0300 0300 7F03 A503 C4FF A907 C3
# 043E2102010301 F2461FBDA1D4 15 0201 04 11FF5900 0100 0300 0300 4C03 6100 BDFF 0F08 CA
# 043E2102010301 71BF99DC8CF7 15 0201 04 11FF5900 0100 0300 0300 F904 8D00 5800 1E08 C4

require 'json'
require 'io/console'

# module providing twos complement helper functions
module TwosComplement
  def convert_to_signed_binary(binary)
    binary_int = binary.to_i(2)
    if binary_int >= 2**15
      return binary_int - 2**16
    else
      return binary_int
    end
  end

  def translate_to_binary(num)
    sprintf("%b", num).rjust(32, '0')
  end
end

# Class that stores packet information in an easily accessible structure
class Packet

  include TwosComplement

  ACCELERATION_FORMAT = "%2.3f"

  attr_reader :timestamp, :prefix, :device_id, :hex_temperature, :hex_x_acc, :hex_y_acc, :hex_z_acc, :rssi

  def initialize(timestamp, prefix, device_id, hex_temperature, hex_x_acc, hex_y_acc, hex_z_acc, hex_rssi)

    # we store both the original hed values (after byte flipping) and calculates the actual values of
    # acceleration and tempeature based on Fujitsu's provided math
    @timestamp = timestamp
    @prefix = prefix
    @device_id = flip_bytes(device_id)
    @hex_temperature = flip_bytes(hex_temperature)
    @hex_x_acc = flip_bytes(hex_x_acc)
    @hex_y_acc = flip_bytes(hex_y_acc)
    @hex_z_acc = flip_bytes(hex_z_acc)
    @hex_rssi = hex_rssi
    @rssi = hex_rssi.to_i(16)

    temperature
    x_acceleration
    y_acceleration
    z_acceleration
  end

  def csv_row
    [
      device_id,
      "%2.2f degF" % temperature,
      ACCELERATION_FORMAT % x_acceleration,
      ACCELERATION_FORMAT % y_acceleration,
      ACCELERATION_FORMAT % z_acceleration,
      rssi,
      timestamp
    ].join(",")
  end

  private

  def flip_bytes(hex_bytes)
    hex_bytes.split("").each_slice(2).map(&:join).reverse.join
  end

  def temperature
    @temperature ||= (((unpack_value(hex_temperature) / 333.87) + 21.0) * 9.0 / 5.0) + 32
  end

  def x_acceleration
    @x_acc ||= acceleration(hex_x_acc)
  end

  def y_acceleration
    @y_acc ||= acceleration(hex_y_acc)
  end

  def z_acceleration
    @z_acc ||= acceleration(hex_z_acc)
  end

  def acceleration(hex_string)
    unpack_value(hex_string) / 2048.to_f
  end

  def unpack_value(hex_string)
    convert_to_signed_binary(translate_to_binary(hex_string.to_i(16))).to_f
  end

end

packets = []

PACKET_DATA_REGEX = %r{^(?<prefix>.{14})(?<device_id>.{12})15020104(?<unused>.{8})010003000300(?<temperature>.{4})(?<x_acc>.{4})(?<y_acc>.{4})(?<z_acc>.{4})(?<rssi>.{2})$}
while line = gets&.chomp do
  begin
    packet_data = JSON.parse(line)
  rescue JSON::ParserError => ex
    puts "ERROR #{ex}"
    # ignore line if we can't parse it
  end

  if (packet_data && (match = PACKET_DATA_REGEX.match(packet_data["packet_data"])))
    timestamp = packet_data["timestamp"]
    prefix = match[:temperature]
    device_id = match[:device_id]
    temperature = match[:temperature]
    x_acc = match[:x_acc]
    y_acc = match[:y_acc]
    z_acc = match[:z_acc]
    rssi = match[:rssi]
    packet = Packet.new(timestamp, prefix,  device_id,  temperature,  x_acc, y_acc,  z_acc, rssi)
    $stdout.puts packet.csv_row
  end
end
