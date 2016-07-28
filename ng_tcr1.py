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
circuito = '''*TCR - Tyristor Controled Reactor

* .------------------------------.
* |      Parametros Gerais       |
* `------------------------------'
.param freq = 60
.param tensao = {500k * sqrt(2/3)}
.param relacao = {500/(18.5*sqrt(3))}

* .---------------------------------.
* | Descricao do circuito principal |
* `---------------------------------'
*Fonte de 500kV/60Hz trifasica
*condicao inicial  = 0V
va pa 0 dc 0 sin(0 {tensao} {freq} 0 0 0)
vb pb 0 dc 0 sin(0 {tensao} {freq} 0 0 -120)
vc pc 0 dc 0 sin(0 {tensao} {freq} 0 0 120)

*varia o angulo de disparo de 170 a 90
vang n_ang 0 dc 0 pwl(0 170 4 90)

*transformador trifasico Y-D 500/18.5kV
*xtrafo_a pa 0 sa sb trafo rel={1/relacao} l_disp=397.88m
xtrafo_a sa sb pa 0 trafo rel={relacao} l_disp=544.7u
xtrafo_b sb sc pb 0 trafo rel={relacao} l_disp=544.7u
xtrafo_c sc sa pc 0 trafo rel={relacao} l_disp=544.7u

*resistores no barramento 18.5kV - somente para medicao
rsa sa 0 10meg
rsb sb 0 10meg
rsc sc 0 10meg

*TCR trifasico no. 1
xtcr1_ab sa sb n_ang tcr freq={freq} v_min=1k
xtcr1_bc sb sc n_ang tcr freq={freq} v_min=1k
xtcr1_ca sc sa n_ang tcr freq={freq} v_min=1k

*medidores de corrente primaria
aipa %vnam(va) i_rmsa med1
aipb %vnam(vb) i_rmsb med1
aipc %vnam(vc) i_rmsc med1

*medidores de tensao primaria
apva %vd(pa pb) v_pa med1
apvb %vd(pb pc) v_pb med1
apvc %vd(pc pa) v_pc med1

*medidores de tensao secundaria
asva %vd(sa sb) v_sa med1
asvb %vd(sb sc) v_sb med1
asvc %vd(sc sa) v_sc med1

*medidores de potencia
apqa pa %vnam(va) ativ_a reat_a med2
apqb pb %vnam(vb) ativ_b reat_b med2
apqc pc %vnam(vc) ativ_c reat_c med2

*---- Componentes utilizados----------------
.model med1 rms(freq = {freq}, pontos = 32)
.model med2 vi_pq(freq = {freq}, pontos = 32)

* .---------------------------------------.
* |Subcircuito: TCR                       |
* |Modela um TCR completo monofasico      |
* `---------------------------------------'
.subckt tcr n_sist1 n_sist2 ang freq=60 v_min=1k

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
Lprinc n_carga n_perda 13.44m ;indutancia de 13.44mH
rperda n_perda n_sist2 0.011	;resistencia de 0.011 ohm em serie

*----circuito de controle-------------------------
adisp %vd(n_sist1 n_sist2) ang gate disparo

*---- Componentes utilizados----------------
.model disparo pfc(freq = {freq}, v_min = {v_min})
.model tiristor scr(ron=0.001, roff=10meg)

.ends

* .---------------------------------------.
* |Subcircuito: Transformador             |
* `---------------------------------------'
* creditos trafo ideal: Kenneth Hatch | Electronic Design
*http://electronicdesign.com/passives/spice-model-ideal-transformer-allows-bi-directional-operation
.subckt trafo h1 h2 x1 x2 rel=1.0 l_disp=1u

*----- trafo ideal -----------
g1 p1 h2 0 inter {rel}
g2 inter 0 x2 x1 1
g3 inter 0 p1 h2 {rel}
g4 x1 x2 inter 0 1
rinter inter 0 1g

*----- indutancia dispersao ----------
ldisp h1 n_res {l_disp}
r1 n_res p1 0.1

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
#spice.limpa_plot()
spice.cmd('ativa = ativ_a + ativ_b + ativ_c')
spice.cmd('reativa = reat_a + reat_b + reat_c')
spice.plotar(['i_rmsa', ], '', 2)
spice.plotar(['ativa', 'reativa' ], '', 3)