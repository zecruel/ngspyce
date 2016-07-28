/*==================================================
Phase-fired controller
For triggering tirystors (SCRs) in AC aplications
==================================================*/

/*=== INCLUDE FILES ====================*/

#include <math.h>
#include <stdlib.h>

/*=== CONSTANTS ========================*/

char *alloc_error_c_tsc = "\n**** Error ****\nC_tsc: Error allocating block storage \n";

/*=== Rotina Principal ===*/

void
cm_c_tsc(ARGS)
{	
	double *rampa;	// calculo da rampa, via integracao
	double *t_ant; 		//tempo anterior
	double d_dt;		//derivada parcial necessaria para integracao
	double *cond;		//memoria de retensao da saida

	if (INIT == 1) {	//primeira chamada do modulo
		// aloca e inicializa a memoria das variaveis
		STATIC_VAR(rampa) = calloc(1, sizeof(double));
		STATIC_VAR(t_ant) = calloc(1, sizeof(double));
		STATIC_VAR(cond) = calloc(1, sizeof(double));
		
		rampa = STATIC_VAR(rampa);
		t_ant = STATIC_VAR(t_ant);
		cond = STATIC_VAR(cond);
		
		// se houver erro, envia mensagem para terminal
		if ((rampa == NULL) || (t_ant == NULL) || (cond == NULL)){ 
			cm_message_send(alloc_error_c_tsc); }
		
		*rampa = 0.0; //inicializa o integrador
		*t_ant = TIME; //incializa a marca de tempo
		*cond = 0.0;	//zera a saida
	}
	
	rampa = STATIC_VAR(rampa);
	t_ant = STATIC_VAR(t_ant);
	cond = STATIC_VAR(cond);
	
	//----------- gera a rampa de comparacao -----------
	d_dt = TIME - *t_ant; // calcula o delta t
	
	if ((fabs(INPUT(v_ref))) < (PARAM(v_min))){ //sincroniza a rampa com o sinal de referencia
		*rampa = 0.0; } 
	else { // a rampa eh gerada por meio de integracao simples
		*rampa = *rampa + d_dt*PARAM(freq)*360.0;} //a amplitude sera de 180 para um semiciclo
	*t_ant = TIME; //guarda a marca de tempo para a proxima iteracao
	//------------------------------------------------------
	
	if ((*rampa >= 90.0) && 
	(fabs(INPUT(v_ref)-INPUT(v_cap)) < PARAM(v_nom)) &&
	(INPUT(comm)>0)) {
		*cond = 1.0;	}//saida
	if ((INPUT(comm)<=0) && (*cond == 1.0)){
		*cond = 0.0;	}//saida
	
	OUTPUT(trig) = *cond;
}
