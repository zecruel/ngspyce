/*==================================================
Implementa um filtro media movel simples (Simple Moving Average)
==================================================*/

/*=== INCLUDE FILES ====================*/

#include <math.h>
#include <stdlib.h>


/*=== CONSTANTS ========================*/

#define erro_max 0.0005  //erro relativo max, para comparacao entre valores float

char *alloc_error_sma = "\n**** Error ****\nSMA: Error allocating block storage \n";


/*=== MACROS ===========================*/


/*=== LOCAL VARIABLES & TYPEDEFS =======*/


/*=== FUNCTION PROTOTYPE DEFINITIONS ===*/


/*=== Rotina Principal ===*/

void
cm_sma(ARGS)
{
	int i;			// iterador
	int pts;		// quantidade de pontos para a janela de media
	int *pos;		// posicao no buffer circular
	double *hist;	// buffer circular, historico dos dados de entrada
	double *prox_t;	// proximo valor de tempo para amostragem
	double erro;	// erro relativo para comparacao de floats
	double total;	// acumulador para calculo da saida
	//char msg[40]; 	// string para envio de mensagens

	pts = PARAM(pontos);	//pega a quant de pontos passada
	if (pts <= 0) { pts = 1;}	//considera que o menor valor eh 1

	if (INIT == 1) {	//primeira chamada do modulo
		// aloca e inicializa a memoria das variaveis
		STATIC_VAR(pos) = calloc(1, sizeof(int));
		STATIC_VAR(hist) = calloc(pts, sizeof(double));
		STATIC_VAR(prox_t) = calloc(1, sizeof(double));
		
		pos = STATIC_VAR(pos);
		hist = STATIC_VAR(hist);
		prox_t = STATIC_VAR(prox_t);
		// se houver erro, envia mensagem para terminal
		if ((pos == NULL) || (hist == NULL) || (prox_t == NULL))
			cm_message_send(alloc_error_sma);
	}
	else {
		pos = STATIC_VAR(pos);
		hist = STATIC_VAR(hist);
		prox_t = STATIC_VAR(prox_t);
	}
	
	//------------------ Rotina de  amostragem ------------------
	if(TIME == 0.0) { //se eh o primeiro
		*prox_t = PARAM(passo); 	// define o proximo tempo
		cm_analog_set_perm_bkpt(*prox_t); // e agenda a interrupcao
		
		hist[*pos] = INPUT(in); //coloca o dado de entrada no historico
		*pos = *pos + 1; // passa para o proximo item do buffer
		if (*pos >= pts) { *pos = 0;} // buffer circular
	}
	else {
		// verifica se o tempo atual eh o tempo agendado
		// a verificacao eh feita atraves de calculo de erro relativo
		erro = fabs((TIME - *prox_t)/ *prox_t); //calcula o erro relativo
		if ( erro < erro_max ){
			*prox_t = TIME + PARAM(passo); 	// define o proximo tempo
			cm_analog_set_perm_bkpt(*prox_t); // e agenda a interrupcao
			
			hist[*pos] = INPUT(in); //coloca o dado de entrada no historico
			*pos = *pos + 1; // passa para o proximo item do buffer
			if (*pos >= pts) { *pos = 0;} // buffer circular
		}
	} //------------------------------------------------------------------
	
	total = 0.0; //inicializa o acumulador para o laco for
	// totaliza o historico dos dados de entrada
	for(i = 0; i < pts; i++) {
		total = total + hist[i];
		// exemplo de mensagem para o terminal:
		//sprintf(msg, "i=%d v=%4.2f t=%4.2f", i , hist[i], total); //retirar
		//cm_message_send(msg);
	}
	OUTPUT(out) = total / pts; //faz a media de saida
}
