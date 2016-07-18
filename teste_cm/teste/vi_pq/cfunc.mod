/*==================================================
Implementa um medidor de Potencias ativa e reativas por amostragem

iteracao em buffer circular:
for (i = 0; i < size; i++) {
    int index = (i + startingPosition) % size;
    // Do stuff with array[index]
}
==================================================*/

/*=== INCLUDE FILES ====================*/

#include <math.h>
#include <stdlib.h>


/*=== CONSTANTS ========================*/

char *alloc_error_vipq = "\n**** Error ****\nVI_PQ: Error allocating block storage \n";


/*=== MACROS ===========================*/


/*=== LOCAL VARIABLES & TYPEDEFS =======*/


/*=== FUNCTION PROTOTYPE DEFINITIONS ===*/


/*=== Rotina Principal ===*/

void
cm_vi_pq(ARGS)
{
	int i;			// iterador
	int index1;	// iterador para buffer circular
	int pts;		// quantidade de pontos para a janela de media
	int *pos;		// posicao no buffer circular
	double *hist_v;	// buffer circular, historico da tensao de entrada
	double *hist_v90;	// buffer circular, historico tensao de entrada defasada
	double *hist_i;		// buffer circular, historico da corrente de entrada
	double *prox_t;	// proximo valor de tempo para amostragem
	double passo;		//passo temporal de amostragem
	double out_p;	// acumulador para calculo de P ativa
	double out_q;	// acumulador para calculo de Q reativa
	double *saida_p; // calculo e retensao do valor P de saida
	double *saida_q; // calculo e retensao do valor Q de saida
	//char msg[40]; 	// string para envio de mensagens

	pts = PARAM(pontos);	//pega a quant de pontos passada
	passo = (double)1/(PARAM(freq)*pts);	//calcula o passo temporal

	if (INIT == 1) {	//primeira chamada do modulo
		// aloca e inicializa a memoria das variaveis
		STATIC_VAR(pos) = calloc(1, sizeof(int));
		STATIC_VAR(hist_v) = calloc(pts, sizeof(double));
		STATIC_VAR(hist_v90) = calloc(pts, sizeof(double));
		STATIC_VAR(hist_i) = calloc(pts, sizeof(double));
		STATIC_VAR(prox_t) = calloc(1, sizeof(double));
		STATIC_VAR(saida_p) = calloc(1, sizeof(double));
		STATIC_VAR(saida_q) = calloc(1, sizeof(double));
		
		pos = STATIC_VAR(pos);
		hist_v = STATIC_VAR(hist_v);
		hist_v90 = STATIC_VAR(hist_v90);
		hist_i = STATIC_VAR(hist_i);
		prox_t = STATIC_VAR(prox_t);
		saida_p = STATIC_VAR(saida_p);
		saida_q = STATIC_VAR(saida_q);
		
		// se houver erro, envia mensagem para terminal
		if ((pos == NULL) || (hist_v == NULL) || (hist_v90 == NULL) ||
			(hist_i == NULL) || (prox_t == NULL) || (saida_p == NULL) ||
			(saida_q == NULL))
		{ cm_message_send(alloc_error_vipq); }
	}
	else {
		pos = STATIC_VAR(pos);
		hist_v = STATIC_VAR(hist_v);
		hist_v90 = STATIC_VAR(hist_v90);
		hist_i = STATIC_VAR(hist_i);
		prox_t = STATIC_VAR(prox_t);
		saida_p = STATIC_VAR(saida_p);
		saida_q = STATIC_VAR(saida_q);
	}
	
	//------------------ Rotina de  amostragem ------------------
	if(TIME == 0.0) { //se eh o primeiro
		*prox_t = passo; 	// define o proximo tempo
		hist_v[*pos] = INPUT(in_v); //coloca o dado de entrada V no historico
		hist_i[*pos] = INPUT(in_i); //coloca o dado de entrada I no historico
		*pos = *pos + 1; // passa para o proximo item do buffer
		if (*pos >= pts) { *pos = 0;} // buffer circular
	}
	else {
		// verifica se o tempo atual eh o tempo agendado
		if (TIME >= *prox_t){
			*prox_t = TIME + passo; 	// define o proximo tempo
			
			hist_v[*pos] = INPUT(in_v); //coloca o dado de entrada V no historico
			
			i = (int)(pts/4);    // defasa de 90 graus (pts/4)
			index1 = (*pos - i) % pts;  // calculo do buffer circular
			if ( index1<0 ){ index1=pts+index1;}
			hist_v90[*pos] = hist_v[index1]; //busca o dado de entrada passado e armazena
			
			hist_i[*pos] = INPUT(in_i); //coloca o dado de entrada I no historico
			
			*pos = *pos + 1; // passa para o proximo item do buffer
			if (*pos >= pts) { *pos = 0;} // buffer circular
			
			//----------- calcula o Valor de P e Q da janela de historico ----------
			out_p = 0.0; //inicializa o acumulador para o laco for
			out_q = 0.0; //inicializa o acumulador para o laco for
			// totaliza o historico dos dados de entrada
			for(i = 0; i < pts; i++) {
				index1 = (i + *pos) % pts;
				out_p = out_p + (hist_v[index1] * hist_i[index1]); //calcula P pela media de V*I
				out_q = out_q + (hist_v90[index1] * hist_i[index1]); //calcula Q pela media de V<90 * I
				
				// exemplo de mensagem para o terminal:
				//sprintf(msg, "i=%d v=%4.2f t=%4.2f", i , hist[i], total); //retirar
				//cm_message_send(msg);
			}
			*saida_p = out_p/pts; //variavel de retencao P
			*saida_q = out_q/pts; //variavel de retencao Q
		}
	} //------------------------------------------------------------------
	
	OUTPUT(out_p) = *saida_p;	//saida via variavel de retensao P
	OUTPUT(out_q) = *saida_q;	//saida via variavel de retensao Q
}
