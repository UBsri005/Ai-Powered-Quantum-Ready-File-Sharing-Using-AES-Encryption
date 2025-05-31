from qiskit.visualization import plot_histogram
import io
from qiskit import QuantumCircuit
import qiskit
print(qiskit.__version__)
#from qiskit_execute import execute
from qiskit import QuantumCircuit, execute


from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


def generate_random_bits(length):
        return ''.join(random.choice('01') for _ in range(length))


def key_(fileName):
    global final_key_int
    num_qubits = 24 
    alice_bits = generate_random_bits(num_qubits)
    alice_circuit = QuantumCircuit(num_qubits, num_qubits)
    alice_circuit.h(range(num_qubits))
    alice_circuit.measure(range(num_qubits), range(num_qubits))
    simulator = Aer.get_backend('qasm_simulator')
    alice_result = execute(alice_circuit, simulator, shots=1).result()
    alice_counts = alice_result.get_counts(alice_circuit)
    
    bob_basis = generate_random_bits(num_qubits)
    bob_circuit = QuantumCircuit(num_qubits, num_qubits)
    for qubit, basis in zip(range(num_qubits), bob_basis):
        if basis == '1':
            bob_circuit.h(qubit)
        bob_circuit.measure(qubit, qubit)
    bob_result = execute(bob_circuit, simulator, shots=1).result()
    bob_counts = bob_result.get_counts(bob_circuit)    
    final_key = [bit for bit, basis in zip(alice_bits, bob_basis) if alice_counts.get(f"{bit}{basis}", 0) == bob_counts.get(f"{bit}{basis}", 0)]
    final_key_int = int(''.join(final_key))   
    final_secret_key = final_key_int.to_bytes((final_key_int.bit_length() + 7) // 5, 'big')
    return final_secret_key    




def encrypt(fileName):
   
    key = key_(fileName)
    with open("uploads/"+ fileName, "rb") as f:
        data = f.read()
    cipher = AES.new(key, AES.MODE_CBC)   
    ciphertext = cipher.encrypt(pad(data, AES.block_size))    
    data = cipher.iv + ciphertext
    print(data)
    with open("uploads/"+ fileName, "wb") as f:
        f.write(data)

    return final_key_int 

def decrypt(fileName, key):
    key = int(key)
    
    cur_key = key.to_bytes((key.bit_length() + 7) // 5, 'big')
    with open("Downloads/"+ fileName, "rb") as f:
        data = f.read()
    iv = data[:AES.block_size]
    cipher = AES.new(cur_key, AES.MODE_CBC, iv)
    decrypted_text = unpad(cipher.decrypt(data[AES.block_size:]), AES.block_size)
    datas = decrypted_text.decode()    
    with open("Downloads/"+ fileName, "w",encoding="utf-8") as f:
        f.write(datas)
