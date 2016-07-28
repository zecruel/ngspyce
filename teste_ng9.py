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
Vi b_mando 0 dc 0 pwl(0 -1 140m 1)

btsc1 l_tsc1 0 v=v(b_mando)<-0.3 ? 1 : 0
btsc2 l_tsc2 0 v=v(b_mando)<-0.6 ? 1 : 0
bconst const 0 v=-0.32*(1+v(l_tsc1)+v(l_tsc2))
bang_c ang_c 0 v=(v(b_mando)-v(const))<0 ? 170 : 170-sqrt((v(b_mando)-v(const))/0.0002)
bang ang 0 v= v(ang_c)<95 ? 95 : (v(ang_c)>170 ? 170 : v(ang_c))

*passo de amostragem = (360pts na freq atual), tempo total de 140ms
.TRAN {1/(freq*360)} 140m

.end
'''
verifica = spice.circ(circuito)
spice.cmd('bg_run')
with spice.ng_livre:
    while not spice.ng_n_exec:
	#print 'esperando'
	spice.ng_livre.wait()
spice.plotar(['ang',],'', 0)