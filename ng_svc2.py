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
*vang n_ang 0 dc 0 pwl(0 170 4 90 4.001 170 8 90 8.001 170 12 90)
Vi b_mando 0 dc 0 pwl(0 -1 12 1)

*liga os TSCs
*vc1 n_c1 0 dc 0 pwl(0 0 4.002 0 4.003 1)
*vc2 n_c2 0 dc 0 pwl(0 0 8 0 8.001 1)

*controlador de suceptancia
xsucp b_mando n_ang n_c1 n_c2 b_ctrl

*transformador trifasico Y-D 500/18.5kV Yd11
*xtrafo_a pa 0 sa sc trafo rel={1/relacao} l_disp=397.88m
*xtrafo_b pb 0 sb sa trafo rel={1/relacao} l_disp=397.88m
*xtrafo_c pc 0 sc sb trafo rel={1/relacao} l_disp=397.88m
xtrafo_a sa sb pa 0 trafo rel={relacao} l_disp={544.7u}
xtrafo_b sb sc pb 0 trafo rel={relacao} l_disp={544.7u}
xtrafo_c sc sa pc 0 trafo rel={relacao} l_disp={544.7u}

*resistores no barramento 18.5kV - somente para medicao
rsa sa 0 10meg
rsb sb 0 10meg
rsc sc 0 10meg

*TCR trifasico no. 1
xtcr1_ab sa sb n_ang tcr freq={freq} v_min=1k
xtcr1_bc sb sc n_ang tcr freq={freq} v_min=1k
xtcr1_ca sc sa n_ang tcr freq={freq} v_min=1k

*TCR trifasico no. 2
xtcr2_ab sa sb n_ang tcr freq={freq} v_min=1k
xtcr2_bc sb sc n_ang tcr freq={freq} v_min=1k
xtcr2_ca sc sa n_ang tcr freq={freq} v_min=1k

*TSC trifasico no. 1
xtsc1_ab sa sb n_c1 tsc freq={freq} v_min=1k v_nom=26k
xtsc1_bc sb sc n_c1 tsc freq={freq} v_min=1k v_nom=26k
xtsc1_ca sc sa n_c1 tsc freq={freq} v_min=1k v_nom=26k

*TSC trifasico no. 2
xtsc2_ab sa sb n_c2 tsc freq={freq} v_min=1k v_nom=26k
xtsc2_bc sb sc n_c2 tsc freq={freq} v_min=1k v_nom=26k
xtsc2_ca sc sa n_c2 tsc freq={freq} v_min=1k v_nom=26k

*filtro 5 harmonico
l5a sa n_l5a 919u
l5b sb n_l5b 919u
l5c sc n_l5c 919u
r5a n_l5a n_c5a 0.001
r5b n_l5b n_c5b 0.001
r5c n_l5c n_c5c 0.001
c5a n_c5a 0 308.869u
c5b n_c5b 0 308.869u
c5c n_c5c 0 308.869u

*filtro 3 harmonico
l3a sa n_l3a 1.907m
l3b sb n_l3b 1.907m
l3c sc n_l3c 1.907m
r3a n_l3a n_c3a 0.001
r3b n_l3b n_c3b 0.001
r3c n_l3c n_c3c 0.001
c3a n_c3a 0 426.916u
c3b n_c3b 0 426.916u
c3c n_c3c 0 426.916u

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

btotal_p p_total 0 v=v(ativ_a)+v(ativ_b)+v(ativ_c)
btotal_q q_total 0 v=v(reat_a)+v(reat_b)+v(reat_c)

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

* .---------------------------------------.
* |Subcircuito: b_ctrl                       |
* |Modela controlador de suceptancia      |
* `---------------------------------------'
.subckt b_ctrl b_mando ang l_tsc1 l_tsc2

rmando b_mando 0 10k

*liga os TSCs
btsc1 l_tsc1 0 v=v(b_mando)<-0.3 ? 1 : 0
rtsc1 l_tsc1 0 10k
btsc2 l_tsc2 0 v=v(b_mando)<-0.6 ? 1 : 0
rtsc2 l_tsc2 0 10k

*calcula
bconst const 0 v=-0.32*(1+v(l_tsc1)+v(l_tsc2))
rconst const 0 10k
bang_c ang_c 0 v=(v(b_mando)-v(const))<0 ? 170 : 170-sqrt((v(b_mando)-v(const))/0.0002)
rang_c ang_c 0 10k

*limita o angulo de disparo de 170 a 90
bang ang 0 v= v(ang_c)<90 ? 90 : (v(ang_c)>170 ? 170 : v(ang_c))
rang l_ang 0 10k

.ends

* .--------------------------------------.
* | Parametros de analise de Transitorio |
* `--------------------------------------'
*ATENCAO: Sempre considerar as condicoes iniciais (parametro uic)
*passo de amostragem = (360pts na freq atual), tempo total de 12s
.save all
.TRAN {1/(freq*360)} 12 uic

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
'''
spice.cmd('rusage time') #verifica o tempo total de simulacao
#spice.limpa_plot()
spice.cmd('ativa = ativ_a + ativ_b + ativ_c')
spice.cmd('reativa = reat_a + reat_b + reat_c')
spice.plotar(['i_rmsa', ], '', 2)
spice.plotar(['ativa', 'reativa' ], '', 3)
'''