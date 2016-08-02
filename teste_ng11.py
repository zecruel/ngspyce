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

*Fontes (condicao inicial igual a zero)
Va pa 0 dc 0 sin(0 8 {freq} 0 0 0)
Vb pb 0 dc 0 sin(0 10 {freq} 0 0 -120)
Vc pc 0 dc 0 sin(0 11 {freq} 0 0 120)

aseq [pa pb pc] [ra rb rc] [ia ib ic] medidor

banga angulo_a 0 v=v(ia)*180/pi
bangb angulo_b 0 v=v(ib)*180/pi
bangc angulo_c 0 v=v(ic)*180/pi

.model medidor seq(freq = {freq}, pontos = 32, r_p = FALSE)

*passo de amostragem = (32pts na freq atual), tempo total de 140ms
.TRAN {1/(freq*32)} 140m uic

.end
'''
verifica = spice.circ(circuito)
spice.cmd('bg_run')
with spice.ng_livre:
    while not spice.ng_n_exec:
	#print 'esperando'
	spice.ng_livre.wait()
spice.plotar(['ra','rb','rc'],'', 0)
spice.plotar(['angulo_a','angulo_b','angulo_c'],'', 1)