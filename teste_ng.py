import ngspyce.ngspyce as ng
import ngspyce.gui as ng_gui
import os

spice = ng.app()
janela = ng_gui.Janela(args=(spice,))

curr_dir_before = os.path.dirname(os.path.abspath(__file__)).replace('\\','/') + '/ngspyce/'
dir_cm = os.path.dirname(os.path.abspath(__file__)).replace('\\','/') + '/ngspyce/lib/ngspice/'
spice.cmd('cd ' + dir_cm)
spice.cmd('codemodel ./analog.cm')
spice.cmd('codemodel ./digital.cm')
spice.cmd('codemodel ./spice2poly.cm')
spice.cmd('codemodel ./xtradev.cm')
spice.cmd('codemodel ./xtraevt.cm')
spice.cmd('cd ' + curr_dir_before + '/teste_cm')

spice.cmd('codemodel ./teste.cm')
spice.cmd('cd ' + curr_dir_before)
circuito = '''*Circuito Basico

.param freq = 60

*Fonte de 3v/60Hz ligada entre o node1 e o GND e defasagem de 90 graus
Vi node1 0 sin(0 3 freq 0 0 90)
RL node1 0 10 ;Resistor de 10 ohms ligado entre o node1 e o GND

*passo de amostragem = (32pts na freq atual), tempo total de 35ms
.TRAN {1/(freq*32)} 35m

.end
'''
verifica = spice.circ(circuito)
spice.cmd('bg_run')
with spice.ng_livre:
    while not spice.ng_n_exec:
	#print 'esperando'
	spice.ng_livre.wait()
spice.plotar(['node1',])

spice.cmd('source ./tcr1.cir')
spice.cmd('bg_run')
with spice.ng_livre:
    while not spice.ng_n_exec:
	spice.ng_livre.wait()
spice.plotar(['i_rms',])