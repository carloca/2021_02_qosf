from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.circuit import Instruction
from typing import List, Tuple


class BellCircuit:
    """
    Class to generate circuit to obtain bell state (|00> + |11>)/sqrt(2) with possibility of errors happening before
    the last cnot gate and different correction methods.
    """

    def __init__(self, n_anc_qubit1: int, n_anc_qubit2: int) -> None:
        self.qubits = QuantumRegister(2, name='qubit')
        # If no error correction, then there are no ancillas
        if n_anc_qubit1 == 0 or n_anc_qubit2 == 0:
            self.anc_qubit = []
        else:
            self.anc_qubit = [QuantumRegister(n_anc_qubit1, name='anc_qb1'),
                              QuantumRegister(n_anc_qubit2, name='anc_qb2')]
        self.cbits = ClassicalRegister(2)

        self.circuit = QuantumCircuit(self.qubits, *self.anc_qubit, self.cbits)

    def add_zero_bf_corr(self, qubit: int, in_place: bool = True) -> QuantumCircuit:
        """
        Add error correction for bit flip when initial state was |0>.

        Circuit:

                                      ┌───┐
                qubit  : ─────■───────┤ X ├──
                            ┌─┴─┐     └─┬─┘
                anc |0>: ───┤ X ├───────■────
                            └───┘

        """
        if qubit not in [1, 2]:
            raise ValueError(f'There are only 2 qubits, so {qubit} is not a valid choice.'
                             f'Please insert 1 or 2!')

        if self.anc_qubit[qubit - 1].size < 1:
            raise Exception(f'This method requires one ancilla per each qubit. '
                            f'Currently qubit {qubit} has {self.anc_qubit[qubit - 1].size} ancillas.')

        circuit = self.circuit.copy()
        circuit.cx(self.qubits[qubit - 1], self.anc_qubit[qubit - 1][0])
        circuit.cx(self.anc_qubit[qubit - 1][0], self.qubits[qubit - 1])

        if in_place:
            self.circuit = circuit

        return circuit

    def add_x_pf_corr(self, qubit: int, in_place: bool = True) -> QuantumCircuit:
        """
        Add error correction for phase flip when initial state was |x>.

        Circuit:

                             ┌───┐               ┌───┐       ┌───┐
                qubit  : ────┤ H ├───────■───────┤ X ├───────┤ H ├───
                             └───┘     ┌─┴─┐     └─┬─┘       └───┘
                anc |0>: ──────────────┤ X ├───────■─────────────────
                                       └───┘

        """
        if qubit not in [1, 2]:
            raise ValueError(f'There are only 2 qubits, so {qubit} is not a valid choice.'
                             f'Please insert 1 or 2!')

        if self.anc_qubit[qubit - 1].size < 1:
            raise Exception(f'This method requires one ancilla per each qubit. '
                            f'Currently qubit {qubit} has {self.anc_qubit[qubit - 1].size} ancillas.')

        circuit = self.circuit.copy()
        circuit.h(self.qubits[qubit - 1])
        circuit.cx(self.qubits[qubit - 1], self.anc_qubit[qubit - 1][0])
        circuit.cx(self.anc_qubit[qubit - 1][0], self.qubits[qubit - 1])
        circuit.h(self.qubits[qubit - 1])

        if in_place:
            self.circuit = circuit

        return circuit

    def add_zero_bf_corr_with_repetition(self, qubit: int, in_place: bool = True) -> QuantumCircuit:
        """
        Add error correction for bit flip when initial state was |0> and error can be also in the ancillas.

        Circuit:

                                                 ┌───┐
                qubit_0  : ──────■───────■───────┤ X ├───────
                               ┌─┴─┐     │       └─┬─┘
                anc_1 |0>: ────┤ X ├─────┼─────────■─────────
                               └───┘   ┌─┴─┐       │
                anc_2 |0>: ────────────┤ X ├───────■─────────
                                       └───┘

        """
        if qubit not in [1, 2]:
            raise ValueError(f'There are only 2 qubits, so {qubit} is not a valid choice.'
                             f'Please insert 1 or 2!')

        if self.anc_qubit[qubit - 1].size < 2:
            raise Exception(f'This method requires two ancilla per each qubit. '
                            f'Currently qubit {qubit} has {self.anc_qubit[qubit - 1].size} ancillas.')

        circuit = self.circuit.copy()
        circuit.cx(self.qubits[qubit - 1], self.anc_qubit[qubit - 1][0])
        circuit.cx(self.qubits[qubit - 1], self.anc_qubit[qubit - 1][1])
        circuit.ccx(self.anc_qubit[qubit - 1][0], self.anc_qubit[qubit - 1][1], self.qubits[qubit - 1])
        if in_place:
            self.circuit = circuit

        return circuit

    def add_x_pf_corr_with_repetition(self, qubit: int, in_place: bool = True) -> QuantumCircuit:
        """
        Add error correction for phase flip when initial state was |x> and error can be also in the ancillas.

        Circuit:

                               ┌───┐                       ┌───┐       ┌───┐
                qubit_0  : ────┤ H ├───────■───────■───────┤ X ├───────┤ H ├───────
                               └───┘     ┌─┴─┐     │       └─┬─┘       └───┘
                anc_1 |0>: ──────────────┤ X ├─────┼─────────■─────────────────────
                                         └───┘   ┌─┴─┐       │
                anc_2 |0>: ──────────────────────┤ X ├───────■─────────────────────
                                                 └───┘

        """
        if qubit not in [1, 2]:
            raise ValueError(f'There are only 2 qubits, so {qubit} is not a valid choice.'
                             f'Please insert 1 or 2!')

        if self.anc_qubit[qubit - 1].size < 2:
            raise Exception(f'This method requires two ancillas per each qubit. '
                            f'Currently qubit {qubit} has {self.anc_qubit[qubit - 1].size} ancillas.')

        circuit = self.circuit.copy()
        circuit.h(self.qubits[qubit - 1])
        circuit.cx(self.qubits[qubit - 1], self.anc_qubit[qubit - 1][0])
        circuit.cx(self.qubits[qubit - 1], self.anc_qubit[qubit - 1][1])
        circuit.ccx(self.anc_qubit[qubit - 1][0], self.anc_qubit[qubit - 1][1], self.qubits[qubit - 1])
        circuit.h(self.qubits[qubit - 1])

        if in_place:
            self.circuit = circuit

        return circuit

    def add_error_gate(self, qubit: QuantumRegister, gate: str) -> None:
        if gate == 'z':
            self.circuit.z(qubit)
        elif gate == 'x':
            self.circuit.x(qubit)

    def add_error(self, qubit: Tuple[int, int], error_gate: str) -> None:
        if qubit[0] not in [1, 2]:
            raise ValueError(f'{qubit[0]} is not a valid choice as qubit value for error error.'
                             f'Please insert 1 or 2!')
        elif len(self.anc_qubit) > 0 and qubit[1] > self.anc_qubit[qubit[0] - 1].size \
                or len(self.anc_qubit) == 0 and qubit[1] != 0:
            raise ValueError(f'In the error correction method  for qubit {qubit[0]} there are '
                             f'{self.anc_qubit[qubit[0] - 1].size if len(self.anc_qubit) > 0 else 0} ancillas, '
                             f'so {qubit[1]} is out of index '
                             f'for applying the error.')
        if qubit[1] == 0:
            self.add_error_gate(self.qubits[qubit[0] - 1], error_gate)
        else:
            # If qubit to apply > 0, then it is an ancilla
            self.add_error_gate(self.anc_qubit[qubit[0] - 1][qubit[1] - 1], error_gate)

    def add_measurement(self, in_pace: bool = True) -> QuantumCircuit:
        """
        Measurement that will return 00 if the state is (|00> + |11>)/sqrt(2).
        """
        circuit = self.circuit.copy()
        circuit.cx(self.qubits[0], self.qubits[1])
        circuit.h(self.qubits[0])
        circuit.measure(self.qubits[:], self.cbits[:])

        if in_pace:
            self.circuit = circuit

        return circuit

    def _prepare_repetition(self, qubit: QuantumRegister, ancillas: QuantumRegister) -> None:
        """
        Circuit to prepare repetition for Shor error correction.
        """

        # Repetition for phase flip
        self.circuit.cx(qubit, ancillas[2])
        self.circuit.cx(qubit, ancillas[5])
        self.circuit.h([qubit, ancillas[2], ancillas[5]])
        self.circuit.barrier()

        # Repetition for bit flip
        self.circuit.cx(qubit, ancillas[:2])
        self.circuit.cx(ancillas[2], ancillas[3:5])
        self.circuit.cx(ancillas[5], ancillas[6:])
        self.circuit.barrier()

    def _add_shor_correction(self, qubit: QuantumRegister, ancillas: QuantumRegister) -> None:
        """
        Circuit for Shor error correction.
        """

        # Correction for bit flip
        self.circuit.cx(qubit, ancillas[:2])
        self.circuit.cx(ancillas[2], ancillas[3:5])
        self.circuit.cx(ancillas[5], ancillas[6:])
        self.circuit.barrier()

        self.circuit.ccx(ancillas[0], ancillas[1], qubit)
        self.circuit.ccx(ancillas[3], ancillas[4], ancillas[2])
        self.circuit.ccx(ancillas[6], ancillas[7], ancillas[5])
        self.circuit.barrier()

        # Correction for phase flip
        self.circuit.h([qubit, ancillas[2], ancillas[5]])
        self.circuit.cx(qubit, ancillas[2])
        self.circuit.cx(qubit, ancillas[5])
        self.circuit.barrier()

        self.circuit.ccx(ancillas[2], ancillas[5], qubit)
        self.circuit.barrier()

    def create_circuit_with_no_correction(self, errors: List[Tuple[Tuple[int, int], str]],
                                          symb_err: bool = False) -> None:
        """
        Create the circuit for obtaining the wanted Bell state with errors before cnot, but no correction.
        """
        self.circuit.h(self.qubits[0])
        self.circuit.barrier()

        if symb_err:
            self.circuit.append(Instruction('err_1', 1, 0, []), [self.qubits[0]])
            self.circuit.append(Instruction('err_2', 1, 0, []), [self.qubits[1]])
            self.circuit.barrier()
        else:
            for qubit, error in errors:
                self.add_error(qubit, error)
            self.circuit.barrier()

        self.circuit.cx(self.qubits[0], self.qubits[1])
        self.circuit.barrier()

        self.add_measurement()

    def create_circuit_with_simple_correction(self, errors: List[Tuple[Tuple[int, int], str]],
                                              symb_err: bool = False) -> None:
        """
        Create the circuit for obtaining the wanted Bell state with errors before cnot and only in the qubits,
        not in the ancillas.
        """
        if self.anc_qubit[0].size < 1 or self.anc_qubit[1].size < 1:
            raise Exception(f'This method requires one ancilla per each qubit. '
                            f'Currently qubit1 has {self.anc_qubit[0].size} ancillas '
                            f'and qubit2 has {self.anc_qubit[1].size} ancillas.')

        self.circuit.h(self.qubits[0])
        self.circuit.barrier()

        if symb_err:
            self.circuit.append(Instruction('err_1', 1, 0, []), [self.qubits[0]])
            self.circuit.append(Instruction('err_2', 1, 0, []), [self.qubits[1]])
            self.circuit.barrier()
        else:
            for qubit, error in errors:
                self.add_error(qubit, error)
            self.circuit.barrier()

        # Add simple correction
        self.add_x_pf_corr(1)
        self.circuit.barrier()
        self.add_zero_bf_corr(2)
        self.circuit.barrier()

        self.circuit.cx(self.qubits[0], self.qubits[1])
        self.circuit.barrier()

        self.add_measurement()

    def create_circuit_with_simple_repetition(self, errors: List[Tuple[Tuple[int, int], str]],
                                              symb_err: bool = False) -> None:
        """
        Create the circuit for obtaining the wanted Bell state with errors before cnot and possible also for ancillas.
        Use assumption on the initial states to simply correction.
        """
        if self.anc_qubit[0].size < 2 or self.anc_qubit[1].size < 2:
            raise Exception(f'This method requires two ancillas per each qubit. '
                            f'Currently qubit1 has {self.anc_qubit[0].size} ancillas '
                            f'and qubit2 has {self.anc_qubit[1].size} ancillas.')

        self.circuit.h(self.qubits[0])
        self.circuit.barrier()

        if symb_err:
            self.circuit.append(Instruction('err_1', 3, 0, []), [self.qubits[0]] + self.anc_qubit[0][:])
            self.circuit.append(Instruction('err_2', 3, 0, []), [self.qubits[1]] + self.anc_qubit[1][:])
            self.circuit.barrier()
        else:
            for qubit, error in errors:
                self.add_error(qubit, error)
            self.circuit.barrier()

        # Add correction
        self.add_x_pf_corr_with_repetition(1)
        self.circuit.barrier()
        self.add_zero_bf_corr_with_repetition(2)
        self.circuit.barrier()

        self.circuit.cx(self.qubits[0], self.qubits[1])
        self.circuit.barrier()

        self.add_measurement()

    def create_circuit_with_shor_correction(self, errors: List[Tuple[Tuple[int, int], str]],
                                            symb_err: bool = False) -> None:
        """
        Create the circuit for obtaining the wanted Bell state with errors before cnot and possible also for ancillas.
        No assumptions are made, so error correction used is Shor one
        (see https://en.wikipedia.org/wiki/Quantum_error_correction#The_Shor_code).
        """
        if self.anc_qubit[0].size < 8 or self.anc_qubit[1].size < 8:
            raise Exception(f'This method requires eight ancillas per each qubit. '
                            f'Currently qubit1 has {self.anc_qubit[0].size} ancillas '
                            f'and qubit2 has {self.anc_qubit[1].size} ancillas.')

        self.circuit.h(self.qubits[0])
        self.circuit.barrier()

        # Prepare repetition state
        self._prepare_repetition(self.qubits[0], self.anc_qubit[0])
        self._prepare_repetition(self.qubits[1], self.anc_qubit[1])

        if symb_err:
            self.circuit.append(Instruction('err_1', 9, 0, []), [self.qubits[0]] + self.anc_qubit[0][:])
            self.circuit.append(Instruction('err_2', 9, 0, []), [self.qubits[1]] + self.anc_qubit[1][:])
            self.circuit.barrier()
        else:
            for qubit, error in errors:
                self.add_error(qubit, error)
            self.circuit.barrier()

        # Add correction
        self._add_shor_correction(self.qubits[0], self.anc_qubit[0])
        self._add_shor_correction(self.qubits[1], self.anc_qubit[1])

        self.circuit.cx(self.qubits[0], self.qubits[1])
        self.circuit.barrier()

        self.add_measurement()
