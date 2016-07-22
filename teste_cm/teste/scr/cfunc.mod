/*==================================================
Silicon Controlled Rectifier tirystor
==================================================*/

/*=== INCLUDE FILES ====================*/

#include <math.h>
#include <stdlib.h>

/*=== CONSTANTS ========================*/

char *alloc_error_scr = "\n**** Error ****\nSCR: Error allocating block storage \n";

/*=== Rotina Principal ===*/

void
cm_scr(ARGS)
{	
	double *res;	// resistencia atual do tiristor
	//char msg[40]; 	// string para envio de mensagens

	if (INIT == 1) {	//primeira chamada do modulo
		// aloca e inicializa a memoria das variaveis
		STATIC_VAR(res) = calloc(1, sizeof(double));
		
		res = STATIC_VAR(res);
		
		// se houver erro, envia mensagem para terminal
		if ((res == NULL))
		{ cm_message_send(alloc_error_scr); }
		
		*res = PARAM(roff); //inicializa a resistencia como desligada
	}
	
	res = STATIC_VAR(res);
	
	if (INPUT(gate) > 0.0) { *res = PARAM(ron);} //conducao
	
	if (INPUT(ak) < 0.0) { *res = PARAM(roff);} //bloqueio
	
	// exemplo de mensagem para o terminal:
		//sprintf(msg, "c= %4.2f", INPUT(ak) * *res); //retirar
		//cm_message_send(msg);
	
	OUTPUT(ak) =  INPUT(ak) * *res;	//saida
	PARTIAL(ak,ak) = *res;
}
