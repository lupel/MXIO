#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import socket
import random
from math import ceil

from main.configuration import Configuration

class Slave:
    def __init__(self, address: bytes):
        """
        This slave unique address
        :param address: 1 byte address
        """
        self.ignore_checksum = Configuration().general.debug
        self.config = Configuration().slave
        if len(address) != 1:
            raise ValueError('Slave: address should be an array with one byte')
        self.address = int(address[0])
        if self.address < 1 or self.address > 247:
            raise ValueError('Slave: address must be in limits [1; 247]')
        self.socket = None
        self.contacts = {}
        self.coils = {}
        self.registers = {}
        self.commands = {
            1: self.read_discrete_output_coils,
            2: self.read_discrete_input_contacts,
            3: self.read_analog_output_holding_registers,
            4: self.read_analog_input_registers,
            5: self.write_single_discrete_output_coil,
            6: self.write_single_analog_output_holding_register,
            15: self.write_multiple_discrete_output_coils,
            16: self.write_multiple_analog_output_holding_registers
        }

    def read_contact(self, index: int) -> bool:
        self.contacts[index] = random.randint(0, 100) >= 50
        return self.contacts[index]

    def read_coil(self, index: int) -> bool:
        if self.config.random and index not in self.coils:
            self.coils[index] = random.randint(0, 100) > 50
        return self.coils.get(index, False)

    def write_coil(self, index: int, state: bool):
        self.coils[index] = state

    def read_register(self, index: int) -> bytes:
        if self.config.random and index not in self.registers:
            self.registers[index] = random.randint(0x0000, 0xFFFF).to_bytes(2, byteorder='big')
        return self.registers.get(index, bytes([0x00, 0x00]))

    def write_register(self, index: int, value: bytes):
        self.registers[index] = bytes([value[0], value[1]])

    def receive(self, slave_address: int, data: bytes):
        """
        Parse incoming bytes
        :param slave_address: First byte
        :param data: All received bytes
        :return: True if there was no errors
        """
        if self.address != slave_address:
            logging.error(f'Slave #{self.address}: command slave_address mismatch: {slave_address}')
            return
        # call appropriate method
        code = int(data[7])
        try:
            response = self.commands[code](data)
        except KeyError:
            logging.error(f'Slave: command code wrong: {code}')
            return bytes([0x80, 0x01])
        except Exception as e:
            logging.error(f'Slave: command error: {str(e)}')
            return False
        return response

    def read_discrete_output_coils(self, request: bytes):
        code = 0x01
        data_address_offset = 1
        response = request[:4]
        # receive data address
        data_address = request[8:10]
        data_address = int(0x0000 | (data_address[0] << 8) | data_address[1]) + data_address_offset
        # receive number of coils to read
        number_of_coils = request[10:12]
        number_of_coils = int(0x0000 | (number_of_coils[0] << 8) | number_of_coils[1])
        asked_data_bytes_len = ceil(number_of_coils/8)
        response += int(asked_data_bytes_len + 3).to_bytes(length=2, byteorder='big')
        response += bytes([self.address, code, asked_data_bytes_len])
        # validate
        try:
            if data_address == 0 or data_address > 9999:
                logging.error(f'command {code}: data_address out of limits: {data_address}')
                raise None
            if number_of_coils == 0 or number_of_coils > 9999:
                logging.error(f'command {code}: number_of_coils out of limits: {number_of_coils}')
                return bytes([0x80, 0x03])
            if data_address + number_of_coils > 10000:
                logging.error(f'command {code}: requested range out of limits: from {data_address} + {number_of_coils}')
                raise None
        except:
            return bytes([0x80, 0x02])
        # read asked coils
        byte = None
        for index in range(data_address, data_address + number_of_coils):
            if (index - data_address) % 8 == 0:
                if byte:  # if it is not first iteration we must append composed byte to response array
                    response += byte
                byte = b'\0'
            if self.read_coil(index):
                byte = bytes([byte[0] | (0x01 << (index - data_address) % 8)])
        response += byte
        return response

    def write_single_discrete_output_coil(self, request: bytes):
        code = 0x05
        data_address_offset = 1
        response = request
        # receive data address
        data_address = request[8:10]
        data_address = int(0x0000 | (data_address[0] << 8) | data_address[1]) + data_address_offset
        # receive value to set
        value = request[10:12]
        value = int(0x0000 | (value[0] << 8) | value[1])
        # validate
        if data_address == 0 or data_address > 9999:
            logging.error(f'command {code}: data_address out of limits: {data_address}')
            return bytes([0x85, 0x02])
        if value == 0xFF00:
            status = True
        elif value == 0x0000:
            status = False
        else:
            logging.error(f'command {code}: status value incorrect: {value.to_bytes(2, byteorder="big").hex()}')
            return bytes([0x85, 0x03])
        # set asked coil state
        self.write_coil(data_address, state=status)
        return response

    def write_multiple_discrete_output_coils(self, request: bytes):
        code = 0x0F
        data_address_offset = 1
        response = request[:4] + (6).to_bytes(2, byteorder='big') + request[6:12]
        # receive data address
        data_address = request[8:10]
        data_address = int(0x0000 | (data_address[0] << 8) | data_address[1]) + data_address_offset
        # receive number of coils
        number_of_coils = request[10:12]
        number_of_coils = int(0x0000 | (number_of_coils[0] << 8) | number_of_coils[1])
        # receive values to set
        try:
            values = request[13:(13 + int(request[12]))]
        except:
            return bytes([0x8F, 0x03])
        # validate
        if data_address == 0 or data_address - data_address_offset + 1 > 9999:
            logging.error(f'command {code}: data_address out of limits: {data_address}')
            return bytes([0x80, 0x02])
        if number_of_coils == 0 or number_of_coils > 9999:
            logging.error(f'command {code}: number_of_coils out of limit: {number_of_coils}')
            return bytes([0x8F, 0x03])
        if data_address + number_of_coils - data_address_offset + 1 > 9999:
            logging.error(f'command {code}: data_address + number_of_coils out of limit: {data_address + number_of_coils - data_address_offset}')
            return bytes([0x8F, 0x02])
        if len(values) != ceil(number_of_coils/8):
            logging.error(f'command {code}: not all values received: {values.hex()}')
            return bytes([0x8F, 0x03])
        # set asked coils
        for index in range(data_address, data_address + number_of_coils):
            self.write_coil(index=index,
                            state=int(values[int((index-data_address) / 8)]) & (0x01 << ((index-data_address) % 8)) > 0)
        return response

    def read_discrete_input_contacts(self, request: bytes):
        code = 0x02
        data_address_offset = 10001
        response = request[:4]
        # receive data address
        data_address = request[8:10]
        data_address = int(0x0000 | (data_address[0] << 8) | data_address[1]) + data_address_offset
        # receive number of coils to read
        number_of_contacts = request[10:12]
        number_of_contacts = int(0x0000 | (number_of_contacts[0] << 8) | number_of_contacts[1])
        asked_data_bytes_len = ceil(number_of_contacts/8)
        response += int(asked_data_bytes_len + 3).to_bytes(length=2, byteorder='big')
        response += bytes([self.address, code, asked_data_bytes_len])
        # validate
        if data_address - data_address_offset + 1 > 9999:
            logging.error(f'command {code}: data_address out of limits: {data_address}')
            return bytes([0x82, 0x02])
        if number_of_contacts == 0 or number_of_contacts > 9999:
            logging.error(f'command {code}: number_of_coils out of limits: {number_of_contacts}')
            return bytes([0x82, 0x03])
        if data_address + number_of_contacts - data_address_offset + 1 > 9999:
            logging.error(f'command {code}: requested range out of limits: from {data_address} + {number_of_contacts}')
            return bytes([0x82, 0x02])
        # read asked coils
        byte = None
        for index in range(data_address, data_address + number_of_contacts):
            if (index - data_address) % 8 == 0:
                if byte:  # if it is not first iteration we must append composed byte to response array
                    response += byte
                byte = b'\0'
            if self.read_contact(index):
                byte = bytes([byte[0] | (0x01 << (index - data_address) % 8)])
        response += byte
        return response

    def read_analog_input_registers(self, request: bytes):
        code = 0x04
        data_address_offset = 30001
        response = request[:4]
        # receive data address
        data_address = request[8:10]
        data_address = int(0x0000 | (data_address[0] << 8) | data_address[1]) + data_address_offset
        # receive number of registers to read
        number_of_registers = request[10:12]
        number_of_registers = int(0x0000 | (number_of_registers[0] << 8) | number_of_registers[1])
        asked_data_bytes_len = number_of_registers*2
        response += int(asked_data_bytes_len + 3).to_bytes(length=2, byteorder='big')
        response += bytes([self.address, code, asked_data_bytes_len])
        # validate
        if data_address - data_address_offset + 1> 9999:
            logging.error(f'command {code}: data_address out of limits: {data_address}')
            return bytes([0x84, 0x02])
        if number_of_registers == 0 or number_of_registers > 9999:
            logging.error(f'command {code}: number_of_registers out of limits: {number_of_registers}')
            return bytes([0x84, 0x03])
        if data_address + number_of_registers - data_address_offset + 1> 9999:
            logging.error(f'command {code}: requested range out of limits: from {data_address} + {number_of_registers}')
            return bytes([0x84, 0x02])
        # read asked registers
        for index in range(data_address, data_address + number_of_registers):
            response += self.read_register(index)
        return response

    def read_analog_output_holding_registers(self, request: bytes):
        code = 0x03
        data_address_offset = 40001
        response = request[:4]
        # receive data address
        data_address = request[8:10]
        data_address = int(0x0000 | (data_address[0] << 8) | data_address[1]) + data_address_offset
        # receive number of registers to read
        number_of_registers = request[10:12]
        number_of_registers = int(0x0000 | (number_of_registers[0] << 8) | number_of_registers[1])
        asked_data_bytes_len = number_of_registers*2
        response += int(asked_data_bytes_len + 3).to_bytes(length=2, byteorder='big')
        response += bytes([self.address, code, asked_data_bytes_len])
        # validate
        if data_address - data_address_offset + 1 > 9999:
            logging.error(f'command {code}: data_address out of limits: {data_address}')
            return bytes([0x83, 0x02])
        if number_of_registers == 0 or number_of_registers > 9999:
            logging.error(f'command {code}: number_of_registers out of limits: {number_of_registers}')
            return bytes([0x83, 0x03])
        if data_address + number_of_registers - data_address_offset > 9999:
            logging.error(f'command {code}: requested range out of limits: from {data_address} + {number_of_registers}')
            return bytes([0x83, 0x02])
        # read asked registers
        for index in range(data_address, data_address + number_of_registers):
            response += self.read_register(index)
        return response

    def write_single_analog_output_holding_register(self, request: bytes):
        code = 0x06
        data_address_offset = 40001
        response = request
        # receive data address
        data_address = request[8:10]
        data_address = int(0x0000 | (data_address[0] << 8) | data_address[1]) + data_address_offset
        # receive value to set
        value = request[10:12]
        value = int(0x0000 | (value[0] << 8) | value[1])
        # validate
        if data_address == 0 or data_address - data_address_offset + 1 > 9999:
            logging.error(f'command {code}: data_address out of limits: {data_address}')
            return bytes([0x86, 0x02])
        # set asked coil state
        self.write_register(index=data_address, value=value.to_bytes(2, byteorder='big'))
        return response

    def write_multiple_analog_output_holding_registers(self, request: bytes):
        code = 0x10
        data_address_offset = 40001
        response = request[:12]
        # receive data address
        data_address = request[8:10]
        data_address = int(0x0000 | (data_address[0] << 8) | data_address[1]) + data_address_offset
        # receive number of registers
        number_of_registers = request[10:12]
        number_of_registers = int(0x0000 | (number_of_registers[0] << 8) | number_of_registers[1])
        # receive values to set
        try:
            values = request[13:(13 + int(request[12]))]
        except Exception as e:
            logging.error(f'command {code}: values subrange taking error: {str(e)}')
            return bytes([0x90, 0x03])
        # validate
        if data_address == 0 or data_address - data_address_offset + 1 > 9999:
            logging.error(f'command {code}: data_address out of limits: {data_address}')
            return bytes([0x90, 0x02])
        if data_address + number_of_registers*2 - data_address_offset + 1 > 9999:
            logging.error(f'command {code}: range out of limits: {data_address+number_of_registers*2-data_address_offset+1}')
            return bytes([0x90, 0x02])
        if len(values) == 0 or len(values) != number_of_registers * 2:
            logging.error(f'command {code}: not enough values bytes: {len(values)}')
            return bytes([0x90, 0x03])
        # set asked coils
        for index in range(data_address, data_address + number_of_registers):
            values_index = (index-data_address)*2
            self.write_register(index=index,
                                value=values[values_index:values_index+2])
        return response
