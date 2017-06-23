import random

OPT = 2
PATIENTS = 5000
FILE_NAME = "parteC"
export = False

class Patient:
    ide = 0
    def __init__(self, Q1):
        self.timeNurseQueue = Q1
        self.timeDoctorQueue = 0
        self.timeNurse = 0
        self.timeDoctor = 0
        self.timeEnd = 0
        self.ide = Patient.ide
        Patient.ide += 1

    @property
    def timeWaiting1(self):
        return self.timeNurse - self.timeNurseQueue

    @property
    def timeWaiting2(self):
        return self.timeDoctor- self.timeDoctorQueue

    @property
    def systemTime(self):
        return self.timeEnd - self.timeNurseQueue

    @property
    def timeWaiting12(self):
        # Retorna tiempo de espera total
        return self.timeWaiting1 + self.timeWaiting2

    def __repr__(self):
        return """
            Paciente numero: {}
            Tiempo de llegada: {}
            Tiempo de espera en cola Nurse: {}


            """.format(
                self.ide, self.timeNurse - self.timeNurseQueue,
                self.timeDoctor - self.timeDoctorQueue
                )


class Attention():
    def __init__(self):
        self.patient = None
        self.queue = []
        self.lastIn = 0
        self.endOfAttention = 0
        self.timeAttending = 0

    def __append__(self, p):
        self.queue.append(p)

class Nurse(Attention):
    def __init__(self):
        super().__init__()

    def timeOfAttention(self, time):
        self.endOfAttention = time + random.uniform(2.5,7.5)

class Doctor(Attention):
    
    def __init__(self):
        super().__init__()

    def timeOfAttention(self, time, opt):
        options = {
        0: random.uniform(8,12),
        1: random.uniform(1,19),
        2: random.expovariate(1/10)
        }
        self.endOfAttention = time + options[opt]

def arrivePatient():
    return random.expovariate(1/15)

if __name__ == "__main__":
    # Tiempo y control de simulacion
    time = 0
    finished = 0
    system = 0
    finishList = []
    nurseQueueAvg = 0 
    doctorQueueAvg = 0
    systemAvg = 0

    # Instancias
    nurse = Nurse()
    doctor = Doctor()

    # Tiempos de llegada/ocurrencia de siguiente evento.
    nextPatient = arrivePatient()

    # Main Loop
    while finished < PATIENTS:
        # print("Tiempo: {}".format(time))
        # print("Cantidad de pacientes ingresados: {}".format(system+finished))
        # print("Cantidad de pacientes en sistema: {}".format(system))
        # print("Cantidad de pacientes finalizados: {}".format(finished))

        # LLegada de paciente
        if nextPatient == time and system + finished < PATIENTS:
            # print("Llego un paciente")
            newPatient = Patient(time) # Inicia el paciente en Q1
            newPatient.timeNurseQueue = time
            nurse.queue.append(newPatient)
            system += 1
            if nurse.patient == None:
                nurse.patient = nurse.queue.pop(0)
                # print("Paciente id: {} entro a Enfermera".format(nurse.patient.ide))
                nurse.patient.timeNurse = time
                nurse.timeOfAttention(time)
                # print("Saldra en el tiempo {}".format(nurse.endOfAttention))
            nextPatient = time + arrivePatient()

        if nurse.patient and nurse.endOfAttention == time:
            doctor.queue.append(nurse.patient)
            nurse.patient.timeDoctorQueue = time
            nurse.patient = None
            if doctor.patient == None:
                doctor.patient = doctor.queue.pop(0)
                # print("Paciente id: {} entro a Doctora".format(doctor.patient.ide)) 
                doctor.patient.timeDoctor = time
                doctor.timeOfAttention(time, OPT)
            
            
            if len(nurse.queue) > 0:
                nurse.patient = nurse.queue.pop(0)
                # print("Paciente id: {} entro a Enfermera".format(nurse.patient.ide))
                nurse.patient.timeNurse = time
                nurse.timeOfAttention(time)


        if doctor.patient and doctor.endOfAttention == time:
            # Sale un paciente
            finished += 1
            system -= 1
            finishList.append(doctor.patient)
            doctor.patient.timeEnd = time
            # print("Paciente id: {} salio de doctora".format(doctor.patient.ide))
            doctor.patient = None

            if len(doctor.queue) > 0:
                doctor.patient = doctor.queue.pop(0)
                # print("Paciente id: {} entro a Doctora".format(doctor.patient.ide))
                doctor.patient.timeDoctor = time
                doctor.timeOfAttention(time, OPT)

        if finished == PATIENTS:
            #Pseudo break
            continue

        times = []
        # Calcular proximo tiempo
        if system + finished < PATIENTS:
            times.append(nextPatient)
        # Verificar si hay pacientes atendiendose
        if nurse.patient:
            times.append(nurse.endOfAttention)
        if doctor.patient:
            times.append(doctor.endOfAttention)
            
        nextTime = min(times)

        # Calcular variables de estado
        if nurse.patient:
            nurse.timeAttending += (nextTime - time)
        if doctor.patient:
            doctor.timeAttending += (nextTime - time)
        nurseQueueAvg += (nextTime - time) * len(nurse.queue)
        doctorQueueAvg += (nextTime - time) * len(doctor.queue)
        systemAvg += (nextTime - time) * system

        time = nextTime

    # Imprimir resultados de pacientes
    waitAvg = 0

    # Exportar CSV de resultados de pacientes
    if export:
        with open("{}.csv".format(FILE_NAME), 'w') as writer:
            writer.write("id,T_cola1,T_enfermera,T_cola2,T_doctora,T_final,T_espera1,T_espera2,T_espera_total,T_total_sistema\n")
            for p in finishList:
                writer.write("{},{},{},{},{},{},{},{},{},{}\n".format(
                    p.ide, p.timeNurseQueue, p.timeNurse, 
                    p.timeDoctorQueue, p.timeDoctor, p.timeEnd, 
                    p.timeWaiting1, p.timeWaiting2, p.timeWaiting12,p.systemTime))


    print("Cantidad de pacientes promedio en cola Enfermera: {}".format(nurseQueueAvg/time))
    print("Cantidad de pacientes promedio en cola Doctora: {}".format(doctorQueueAvg/time))
    print("Cantidad de pacientes promedio en el sistema: {}".format(systemAvg/time))
    print("Utilizacion promedio Enfermera: {}".format(nurse.timeAttending/time))
    print("Utilizacion promedio Doctora: {}".format(doctor.timeAttending/time))



