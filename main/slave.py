#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import socket
import crcmod.predefined
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
        self.coils = {}
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

    def get_coil(self, index: int):
        return self.coils.get(index, False)

    def set_coil(self, index: int, state: bool):
        self.coils[index] = state

    def check_crc(self, data: bytes, crc: bytes) -> bool:
        return self.ignore_checksum or Slave.calculate_crc(data) == crc

    @staticmethod
    def calculate_crc(data: bytes) -> bytes:
        crc16 = crcmod.predefined.Crc('modbus')
        crc16.update(data)
        checksum = crc16.digest()
        return bytes([checksum[1], checksum[0]])

    def receive(self, slave_address: int, client: socket.socket):
        """
        Parse incoming bytes
        :param slave_address: First byte
        :param client: Socket to work with
        :return: True if there was no errors
        """
        if self.address != slave_address:
            logging.error(f'Slave #{self.address}: command slave_address mismatch: {slave_address}')
            return
        command = client.recv(1)
        if not command or command == b'':
            logging.error('Slave: command was not received')
            return False
        # call appropriate method
        code = int(command[0])
        try:
            response = self.commands[code](client)
        except KeyError:
            logging.error(f'Slave: command code wrong: {code}')
            return False
        except Exception as e:
            logging.error(f'Slave: command error: {str(e)}')
            return False
        return response

    def read_discrete_output_coils(self, s: socket.socket):
        code = 0x01
        request = bytes([self.address, code])
        response = bytes([self.address, code])
        # receive data address
        data_address = s.recv(2)
        if not data_address or data_address == b'':
            raise Exception(f'command {code}: data_address was not received')
        request += data_address
        data_address = int(0x0000 | (data_address[0] << 8) | data_address[1]) + 1
        # receive number of coils to read
        number_of_coils = s.recv(2)
        if not number_of_coils or number_of_coils == b'':
            raise Exception(f'command {code}: number_of_coils was not received')
        request += number_of_coils
        number_of_coils = int(0x0000 | (number_of_coils[0] << 8) | number_of_coils[1])
        response += bytes([ceil(number_of_coils/8)])
        # read CRC
        crc = s.recv(2)
        if not crc or crc == b'':
            raise Exception(f'command {code}: crc was not received')
        if not self.check_crc(data=request, crc=crc):
            raise Exception(f'command {code}: crc check failed: request={request.hex()}; crc={crc.hex()}')
        # validate
        if data_address > 9999:
            raise Exception(f'command {code}: data_address out of limits: {data_address}')
        if number_of_coils > 9998:
            raise Exception(f'command {code}: number_of_coils out of limits: {number_of_coils}')
        if data_address + number_of_coils > 9999:
            raise Exception(f'command {code}: requested range out of limits: from {data_address} + {number_of_coils}')
        # read asked coils
        byte = None
        for index in range(data_address, data_address+number_of_coils+1):
            if (index - data_address) % 8 == 0:
                if byte:  # if it is not first iteration we must append composed byte to response array
                    response += byte
                byte = b'\0'
            if self.get_coil(index):
                byte = bytes([byte[0] | (0x01 << (index - data_address) % 8)])
        response += byte
        # append crc
        response += Slave.calculate_crc(data=response)
        return response

    def write_single_discrete_output_coil(self, s: socket.socket):
        logging.debug('Debug slave.write_single_discrete_output_coil')
        code = 0x05
        request = bytes([self.address, code])
        response = bytes([self.address, code])
        # receive data address
        data_address = s.recv(2)
        if not data_address or data_address == b'':
            raise Exception(f'command {code}: data_address was not received')
        request += data_address
        response += data_address
        data_address = int(0x0000 | (data_address[0] << 8) | data_address[1]) + 1
        # receive number of coils to read
        status = s.recv(2)
        if not status or status == b'':
            raise Exception(f'command {code}: status was not received')
        request += status
        response += status
        # read CRC
        crc = s.recv(2)
        if not crc or crc == b'':
            raise Exception(f'command {code}: crc was not received')
        if not self.check_crc(data=request, crc=crc):
            raise Exception(f'command {code}: crc check failed: request={request.hex()}; crc={crc.hex()}')
        # validate
        if data_address > 9999 or data_address == 0:
            raise Exception(f'command {code}: data_address out of limits: {data_address}')
        if status[0] & 0xFF == 0xFF and status[1] & 0xFF == 0x00:
            status = True
        elif status[0] | status[1] & 0xFF == 0x00:
            status = False
        else:
            raise Exception(f'command {code}: status value incorrect: {status.hex()}')
        # set asked coil state
        self.set_coil(data_address, state=status)
        # append crc
        response += Slave.calculate_crc(data=response)
        return response

    def write_multiple_discrete_output_coils(self, s: socket.socket):
        logging.debug('Implement slave.write_multiple_discrete_output_coils')
        pass

    def read_discrete_input_contacts(self, s: socket.socket):
        logging.debug('Implement slave.read_discrete_input_contacts')
        pass

    def read_analog_input_registers(self, s: socket.socket):
        logging.debug('Implement slave.read_analog_input_registers')
        pass

    def read_analog_output_holding_registers(self, s: socket.socket):
        logging.debug('Implement slave.read_analog_output_holding_registers')
        pass

    def write_single_analog_output_holding_register(self, s: socket.socket):
        logging.debug('Implement slave.write_single_analog_output_holding_register')
        pass

    def write_multiple_analog_output_holding_registers(self, s: socket.socket):
        logging.debug('Implement slave.write_multiple_analog_output_holding_registers')
        pass

