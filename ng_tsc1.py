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
circuito = '''*TSC - Tyristor Swicthed Capacitor

* .------------------------------.
* |      Parametros Gerais       |
* `------------------------------'
.param freq = 60

* .---------------------------------.
* | Descricao do circuito principal |
* `---------------------------------'
*Fonte de 18.5kV/60Hz ligada entre o n_sist1 e o GND
*condicao inicial  = 0V
vi n_fonte 0 dc 0 sin(0 26.163k freq 0 0)

*varia o angulo de disparo de 170 a 90
vang n_ang 0 dc 0 pwl(0 0 0.5 0 0.501 1 2 1 2.001 0 3 0 3.001 1 4 1)

xtsc1 n_fonte 0 n_ang tsc freq={freq} v_min=1k v_nom=26k

amed1 %vnam(vi) i_rms med1

amed2 n_fonte %vnam(vi) tsc_p tsc_q med2

*---- Componentes utilizados----------------
.model med1 rms(freq = {freq}, pontos = 32)
.model med2 vi_pq(freq = {freq}, pontos = 32)

* .---------------------------------------.
* |Subcircuito: TSC                       |
* |Modela um TSC completo monofasico      |
* `---------------------------------------'
.subckt tsc n_sist1 n_sist2 liga freq=60 v_min=1k v_nom=10k

*----Valvula----------------------------------
*--- tiristor semiciclo positivo
ascr_p n_sist1 n_carga gate tiristor

*--- tiristor semiciclo negativo
ascr_n n_carga n_sist1 gate tiristor

*--snuber-------------------------------------
rs n_sist1 n_snuber 1k
cs n_snuber n_carga 0.11u

*----resistencia de carga - paralelo ao indutor---------------
rpar n_carga n_sist2 100meg ;Resistor de 10mega ohms ligado entre o n_carga e o GND

*----indutor de carga----------------------------------------------
Lprinc n_carga n_perda 4.002m ;indutancia de 4.002mH
rperda n_perda n_cap 0.011	;resistencia de 0.011 ohm em serie
cprinc n_cap n_sist2 216.479u ic={-v_nom}

*----circuito de controle-------------------------
adisp %vd(n_sist1 n_sist2) %vd(n_cap n_sist2) liga gate disparo

*---- Componentes utilizados----------------
.model disparo c_tsc(freq = {freq}, v_min = {v_min}, v_nom = {v_nom})
.model tiristor scr(ron=0.001, roff=10meg)

.ends

* .--------------------------------------.
* | Parametros de analise de Transitorio |
* `--------------------------------------'
*ATENCAO: Sempre considerar as condicoes iniciais (parametro uic)
*passo de amostragem = (360pts na freq atual), tempo total de 4s
.save all
.TRAN {1/(freq*360)} 4 uic

* .--------------------------------------.
* |             ---- FIM ---             |
* `--------------------------------------'
.end
'''
verifica = spice.circ(circuito)
spice.cmd('bg_run')
with spice.ng_livre:
    while not spice.ng_n_exec:
	#print 'esperando'
	spice.ng_livre.wait()

spice.cmd('rusage time') #verifica o tempo total de simulacao
spice.cmd('a = n_ang * 10000')
spice.plotar(['i_rms', ], '', 2)
spice.plotar(['a', 'n_fonte', 'xtsc1.n_cap'], '', 3)
spice.plotar(['tsc_p', 'tsc_q' ], '', 1)