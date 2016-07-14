
from ctypes import CDLL, CFUNCTYPE, Structure, c_int, c_char_p, c_void_p, \
        c_bool, c_double, POINTER, c_short, cast
import re
import os
import time
import Queue
import subprocess
import threading

# enum dvec_flags {
#...
# };
class dvec_flags(object):
   vf_real = (1 << 0)       # The data is real.
   vf_complex = (1 << 1)    # The data is complex. 
   vf_accum = (1 << 2)      # writedata should save this vector.
   vf_plot = (1 << 3)       # writedata should incrementally plot it.
   vf_print = (1 << 4)      # writedata should print this vector.
   vf_mingiven = (1 << 5)   # The v_minsignal value is valid.
   vf_maxgiven = (1 << 6)   # The v_maxsignal value is valid.
   vf_permanent = (1 << 7)  # Don't garbage collect this vector.

# enum simulation_types {
#   ...
# };
class simulation_type(object):
    notype = 0
    time = 1
    frequency = 2
    voltage = 3
    current = 4
    output_n_dens = 5
    output_noise = 6
    input_n_dens = 7
    input_noise = 8
    pole = 9
    zero = 10
    sparam = 11
    temp = 12
    res = 13
    impedance = 14
    admittance = 15
    power = 16
    phase = 17
    db = 18
    capacitance = 19
    charge = 20

class ngcomplex(Structure):
    _fields_ = [
	('cx_real', c_double),
	('cx_imag', c_double)]

class vector_info(Structure): # acesso a um unico vetor
    _fields_ = [
	('v_name', c_char_p), # Same as so_vname
	('v_type', c_int), # Same as so_vtype
	('v_flags', c_short), # Flags (a combination of VF_*)
	('v_realdata', POINTER(c_double)), # Real data
	('v_compdata', POINTER(ngcomplex)), # Complex data
	('v_length', c_int)] #Length of the vector

class dvec (Structure): # dados de um vetor de simulacao
    _fields_ = [
	('v_name', c_char_p), # Same as so_vname
	('v_type', c_int), # Same as so_vtype
	('v_flags', c_short), # Flags (a combination of VF_*)
	('v_realdata', POINTER(c_double)), # Real data
	('v_compdata', POINTER(ngcomplex)), # Complex data
	('v_minsignal', c_double), # Minimum value to plot.
	('v_maxsignal', c_double), # Maximum value to plot.
	('v_gridtype', c_int),	# One of GRID_*.
	('v_plottype', c_int),	#	 One of PLOT_*.
	('v_length', c_int),	# Length of the vector.
	('v_rlength', c_int),	# How much space we really have.
	('v_outindex', c_int),	# Index if writedata is building the vector.
	('v_linestyle', c_int),	# What line style we are using.
	('v_color', c_int),	# What color we are using.
	('v_defcolor', c_char_p), # The name of a color to use.
	('v_numdims', c_int),	# How many dims -- 0 = scalar (len = 1).
	('v_dims', c_int * 8),	# The actual size in each dimension. (MAXDIMS=8)
	('v_plot', c_void_p), # The plot structure (if it has one).
	('v_nex', c_void_p), # Link for list of plot vectors.
	('v_link2', c_void_p), # Extra link for things like print.
	('v_scale', c_void_p)] # If this has a non-standard scale...

class vecinfo(Structure): # acesso a um vetor dentro de um conjunto de simulacoes
    _fields_ = [
	('number', c_int), # number of vector, as position in the linked list of vectors, stats with 0 (zero)
	('name', c_char_p), # name of a actual vector
	('is_real', c_bool), # TRUE if the actual vector has real data
	('dvec', POINTER(POINTER(dvec))), # a void pointer to struct dvec *d, the actual vector
	('dvecscale', POINTER(POINTER(dvec)))] # a void pointer to struct dvec *ds, the scale vector

class vecinfoall(Structure): # acesso a um conjunto de simulacoes
    _fields_ = [
	# the plot
	('name', c_char_p),
	('title', c_char_p),
	('date', c_char_p),
	('type', c_char_p),
	('veccount', c_int),
	# the data as an array of vecinfo with length equal to the number of vectors in the plot
	('vecs', POINTER(POINTER(vecinfo)))]

class vecvalues(Structure): # acesso a um unico valor dentro de um vetor especifico
    _fields_ = [
	('name', c_char_p), # name of a specific vector
	('creal', c_double), # actual data value
	('cimag', c_double), # actual data value 
	('is_scale', c_bool), # if 'name' is the scale vector
	('is_complex', c_bool)] # if the data are complex numbers 

class vecvaluesall(Structure): # acesso a  uma colecao de vetores
    _fields_ = [
	('veccount', c_int), # number of vectors in plot
	('vecindex', c_int), #  index of actual set of vectors. i.e. the number of accepted data points
	('vecsa', POINTER(POINTER(vecvalues)))] # values of actual set of vectors, indexed from 0 to (veccount - 1)

class app:
	
	#globais
	log = Queue.Queue() #o log vai para uma pilha queue
	i_vetores ={} #dicionario que lista o nome e o indice de cada vetor disponivel
	vetores ={} #dicionario que lista o nome  e a estrutura vecvalues de cada vetor disponivel
	ng_n_exec = True #indica que o ngspice nao esta em execucao
	ng_livre = threading.Condition() #indica que o ngspice esta livre
	
	def __init__(self):
		self.dir = os.path.dirname(os.path.abspath(__file__)).replace('\\','/') + '/'
		#------------------------------------------------------------------------------------
		# inicializacao
		
		# Carrega  o dll
		dir_spice = os.path.dirname(os.path.abspath(__file__)) .replace('\\','/') + '/'
		#spice_lib_dir = dir_spice + 'share/ngspice/'
		if os.name == 'posix':			
			dir_dll = dir_spice + 'lib/'
			ngspice_dll = 'libngspice.so.0.0.0'
		else:
			dir_dll = dir_spice + 'bin/'
			ngspice_dll = 'libngspice-0.dll'
		path_dll = dir_dll + ngspice_dll
		if not os.path.exists(path_dll):
		    #Give up if none of the above succeeded:
		    raise Exception('Could not locate ' + path_dll)
		curr_dir_before = os.getcwd()
		os.chdir(dir_dll)

		#os.putenv('SPICE_LIB_DIR',  spice_lib_dir)
		#os.environ['SPICE_LIB_DIR'] =  spice_lib_dir
		#os.environ['NGSPICE_INPUT_DIR'] =  spice_lib_dir
		if os.name == 'posix':
			self.spice = CDLL(path_dll)
		else:
			self.spice = CDLL(ngspice_dll)
		os.chdir(curr_dir_before)
		
		# inicializa o NGspice
		self.spice.ngSpice_Init(self.printfcn, self.statfcn, self.spice_exit, self.data_rt, self.init_rt, self.bg_running, None)
		
		# configura o regex
		self.end_regex = re.compile('.end', flags = re.IGNORECASE)
		
		#-------------------------------------------------------------------------------------
		# definicao da funcoes a serem chamadas
		
		#argtypes traduz o tipo esperado de parametros a serem passados
		#restype traduz o tipo a ser retornado
		
		# int  ngSpice_Command(char* command);
		self.spice.ngSpice_Command.argtypes = [c_char_p] # envia um comando para o spice
		
		# int ngSpice_Circ(char**)
		self.spice.ngSpice_Circ.argtypes = [POINTER(c_char_p)]
		
		#bool ngSpice_running(void)
		self.spice.ngSpice_running.restype = c_bool
		
		#
		self.spice.ngSpice_AllPlots.restype = POINTER(c_char_p)
		
		# /* get info about a vector */
		# pvector_info ngGet_Vec_Info(char* vecname);
		self.spice.ngGet_Vec_Info.restype = POINTER(vector_info)
		self.spice.ngGet_Vec_Info.argtypes = [c_char_p]
		
		self.spice.ngSpice_AllVecs.argtypes = [c_char_p]
		self.spice.ngSpice_AllVecs.restype = POINTER(c_char_p)
		self.spice.ngSpice_CurPlot.restype = c_char_p
	# ------------------------------------------------------------------------------------
	# Estruturas do NGSpice

	# Unit names for use with pint or other unit libraries
	vector_type = [
	    'dimensionless',      # notype = 0
	    'second',             # time = 1
	    'hertz',              # frequency = 2
	    'volt',               # voltage = 3
	    'ampere',             # current = 4
	    'NotImplemented',     # output_n_dens = 5
	    'NotImplemented',     # output_noise = 6
	    'NotImplemented',     # input_n_dens = 7
	    'NotImplemented',     # input_noise = 8
	    'NotImplemented',     # pole = 9
	    'NotImplemented',     # zero = 10
	    'NotImplemented',     # sparam = 11
	    'NotImplemented',     # temp = 12
	    'ohm',                # res = 13
	    'ohm',                # impedance = 14
	    'siemens',            # admittance = 15
	    'watt',               # power = 16
	    'dimensionless'       # phase = 17
	    'NotImplemented',     # db = 18
	    'farad'               # capacitance = 19
	    'coulomb'             # charge = 21           
	]

	# ------------------------------------------------------------------------------------
	# Funcoes de retorno (callbaks)
	
	@staticmethod
	@CFUNCTYPE(c_int, c_char_p, c_int, c_void_p)
	def printfcn(output, id, ret):
	    """Callback for libngspice to print a message"""	    
	    if output.startswith(b'stderr'):
		app.log.put('ALERTA: '+ output[7:].decode('ascii'))
	    else:
		app.log.put(output[7:].decode('ascii'))
	    return 0
	    
	@staticmethod
	@CFUNCTYPE(c_int, c_char_p, c_int, c_void_p)
	def statfcn(status, id, ret): 
	    """Callback for libngspice to report the current status"""
	    app.log.put(status.decode('ascii'))
	    return 0
	    
	@staticmethod
	@CFUNCTYPE(c_int, c_int, c_bool, c_bool, c_int, c_void_p)
	def spice_exit(status, immediate, quit, id, ret): 
	    """Callback for libngspice to report fatal error in execution"""
	    app.log.put('ERRO: NGspice saiu inesperadamente. Cod erro ' + str(status))
	    return 0
	
	@staticmethod
	@CFUNCTYPE(c_int, POINTER(vecvaluesall), c_int, c_int, c_void_p)
	def data_rt(a_vet, a_vet_len, id, ret): 
	    """callback function for sending an array of structs containing data values 
	    of all vectors in the current plot (simulation output) (NULL allowed)"""
	    
	    geral = a_vet.contents  #estrutura geral
	    #abaixo os campos da estrutura geral
	    num_vet = geral.veccount #numero de vetores
	    i_atual = geral.vecindex	   # indice do ponto em relacao a simulacao total
	    lista_vet = geral.vecsa	#lista de ponteiros das estruturas de vetores
	    #i=0
	    #vetor = lista_vet[i].contents #acesso a estrutura do vetor indexado por i
	    # abaixo os campos do vetor atual
	    #nome = vetor.name
	    #real = vetor.creal
	    #imag = vetor.cimag
	    #escala = vetor.is_scale
	    #complex = vetor.is_complex
	    #app.vetores = {}
	    for i in range(num_vet):
		    #constroi o dicionario de vetores com nome e indice
		    vetor = lista_vet[i].contents 
		    app.vetores[vetor.name] = vetor
	    
	    #app.log.put('Vetor ' + str(i) + ': '+ nome +' = '+ str(real) + ' ' + str(imag) + 'i')
	    
	    return 0
	    
	@staticmethod
	@CFUNCTYPE(c_int, POINTER(vecinfoall), c_int, c_void_p)
	def init_rt(vet_info, id, ret):
	    
	    geral = vet_info.contents  #estrutura geral
	    #abaixo os campos da estrutura geral
	    nome = geral.name
	    titulo = geral.title
	    data = geral.date
	    tipo = geral.type
	    num_vet = geral.veccount
	    lista_vet = geral.vecs	#lista de ponteiros das estruturas de info vetores
	    #i_vetor = lista_vet[i].contents #acesso a estrutura do vetor indexado por i
	    # abaixo os campos do vetor atual
	    #i_num = i_vetor.number
	    #i_nom = i_vetor.name
	    #i_real = i_vetor.is_real
	    #i_dvec = i_vetor.dvec
	    #i_dvecs = i_vetor.dvecscale
	    app.i_vetores = {}
	    app.vetores = {}
	    for i in range(num_vet):
		    #constroi o dicionario de vetores com nome e indice
		    i_vetor = lista_vet[i].contents 
		    app.i_vetores[i_vetor.name] = i_vetor.number
		    app.vetores[i_vetor.name] = i_vetor.number
	    #app.log.put('INIT '+nome+titulo+data+tipo)
	    #app.log.put('Vetor '+ repr(app.i_vetores))
	    
	    return 0
	
	@staticmethod
	@CFUNCTYPE(c_int, c_bool, c_int, c_void_p)
	def bg_running(run, id, ret): 
	    """indicate if background thread is running"""
	    app.ng_n_exec = run
	    if run:
		    with app.ng_livre:
			    app.ng_livre.notify()
	    #print run
	    return 0

	#--------------------------------------------------------------------------------

	def cmd(self, command):
	    """Send a commang to the ngspice engine"""
	    self.spice.ngSpice_Command(command.encode('ascii'))
	    time.sleep(0.1)

	def circ(self, netlist_lines):
	    """Specify a netlist"""
	    # Accept an array of lines, or a multi-line string
	    if issubclass(type(netlist_lines), str):
		netlist_lines = netlist_lines.split('\n')
	    '''
	    # First line is ignored by the engine
	    netlist_lines.insert(0, '* First line')
	    # Add netlist end
	    if not any((end_regex.match(line) for line in netlist_lines)):
		netlist_lines.append('.end')
	    '''
	    netlist_lines = [line.encode('ascii') for line in netlist_lines]
	    # Add list terminator
	    netlist_lines.append(None)
	    array = (c_char_p * len(netlist_lines))(*netlist_lines)
	    return self.spice.ngSpice_Circ(array)

	def plots(self):
	    """List available plots (result sets)"""
	    ret = []
	    plotlist = self.spice.ngSpice_AllPlots()
	    ii = 0
	    while True:
		if not plotlist[ii]:
		    return ret
		ret.append(plotlist[ii].decode('ascii'))
		ii += 1

	def vectorNames(self, plot=None):
	    """List the vectors present in the specified plot 
	    
	    List the voltages, currents, etc present in the specified plot.
	    Defaults to the last plot.
	    """
	    names = []
	    if (plot is None) | (plot == ''):
		plot = self.spice.ngSpice_CurPlot()
	    veclist = self.spice.ngSpice_AllVecs(plot)
	    ii = 0
	    while True:
		if not veclist[ii]:
		    return names
		names.append(veclist[ii].decode('ascii'))
		ii += 1

	def vectors(self, names=None):
	    """Return a dictionary with the specified vectors
	    
	    If names is None, return all available vectors"""
	    if names is None:
		plot = self.spice.ngSpice_CurPlot()
		names = self.vectorNames(plot)
	    return dict(zip(names, map(vector, names)))

	def vector(self, name):
	    """Return a numpy.ndarray with the specified vector"""
	    # modificado para retirar a dependencia do numpy
	    vec = self.spice.ngGet_Vec_Info(name.encode('ascii'))
	    if not vec:
		raise RuntimeError('Vector {} not found'.format(name))
	    vec = vec[0]
	    if vec.v_length == 0:
		array = None
	    elif vec.v_flags & dvec_flags.vf_real:
		array = []
		for i in range(vec.v_length):
			array.append(vec.v_realdata[i])
	    elif vec.v_flags & dvec_flags.vf_complex:
		array = []
		for i in range(vec.v_length):
			array.append(vec.v_compdata[i])
	    else:
		raise RuntimeError('No valid data in vector')
	    app.log.put('Fetched vector {} type {}'.format(name, vec.v_type))
	    return array
	    
	def plotar(self, lista, plot = ''):
		arq_data = self.dir + 'plot'
		arq_gnu = self.dir + 'gnu_com'
		
		if len(lista) > 0:
			if plot != '':
				self.cmd('setplot ' + plot)			
			comm_spice = 'wrdata ' + arq_data
			for i in lista:
				comm_spice = comm_spice + ' ' + str(i)
			self.cmd(comm_spice)
			
			p_plot = 'plot '
			for i in range(len(lista)):
				p_plot = p_plot + '"' + arq_data + '.data" using '
				p_plot = p_plot + str(1+i*2) + ':' + str(2+i*2)
				p_plot = p_plot + ' title "' + str(lista[i]) + '" with lines'
				if i < (len(lista)-1):
					p_plot = p_plot + ', \\\n'
			
			with open(arq_gnu, 'w') as file_:
				file_.write(p_plot)

			proc = subprocess.Popen(['E:/documentos/prog/contrade/gnuplot/bin/gnuplot.exe -persist ' + arq_gnu], shell=True,
					stdin=None, stdout=None, stderr=None, close_fds=True)
    
if __name__ == "__main__":
    import gui
    print 'Modulo de interface ao simulador de circuitos NGSpice.'
    ''' o codigo abaixo eh somente para teste '''
    spice = app()
    janela = gui.Janela(args=(spice,))
