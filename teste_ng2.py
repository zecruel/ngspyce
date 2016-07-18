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
*Vi node1 0 dc 0 sin(0 3 freq 0 0 90)

*fonte de comportamento nao linear
*
bi fonte 0 v=sin(2*pi*freq*time)*(time<70m ? 3 : 2)
* fonte senoidal com amplitude de 3V ate 70ms e 2V dai por diante

RL fonte res 10 ;Resistor de 10 ohms ligado entre a fonte e o medidor
amed fonte %id(res 0) ativ reat medidor ;medidor ligado entre o resitor e o GND
rp ativ 0 10k
rq reat 0 10k

.model medidor vi_pq(freq = 60, pontos = 32)

*passo de amostragem = (32pts na freq atual), tempo total de 140ms
.TRAN {1/(freq*32)} 140m

.end
'''
verifica = spice.circ(circuito)
spice.cmd('bg_run')
with spice.ng_livre:
    while not spice.ng_n_exec:
	#print 'esperando'
	spice.ng_livre.wait()
spice.cmd('apar = fonte * -bi#branch')
#spice.plotar(['fonte','apar'])
spice.plotar(['apar', 'ativ', 'reat'])