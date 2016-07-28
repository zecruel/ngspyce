/*==================================================
Implementa um medidor RMS por amostragem

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

#define erro_max 0.0005  //erro relativo max, para comparacao entre valores float

char *alloc_error_rms = "\n**** Error ****\nRMS: Error allocating block storage \n";


/*=== MACROS ===========================*/


/*=== LOCAL VARIABLES & TYPEDEFS =======*/


/*=== FUNCTION PROTOTYPE DEFINITIONS ===*/


/*=== Rotina Principal ===*/

void
cm_rms(ARGS)
{
	int i;			// iterador
	int index1;	// iterafor para buffer circular
	int index2;	// iterafor para buffer circular
	int pts;		// quantidade de pontos para a janela de media
	int *pos;		// posicao no buffer circular
	double *hist;	// buffer circular, historico dos dados de (entrada)^2
	double *hist_t;	// buffer circular, historico dos tempos de aquisicao
	double *prox_t;	// proximo valor de tempo para amostragem
	double passo;		//passo temporal de amostragem
	double total;	// calculo da integral de (entrada)^2
	double total_t;	// acumulador para calculo do periodo
	double *saida; // calculo e retensao do valor RMS de saida
	//char msg[40]; 	// string para envio de mensagens

	pts = PARAM(pontos)-1;	//pega a quant de pontos passada
	passo = (double)1/(PARAM(freq)*(pts+1));	//calcula o passo temporal

	if (INIT == 1) {	//primeira chamada do modulo
		// aloca e inicializa a memoria das variaveis
		STATIC_VAR(pos) = calloc(1, sizeof(int));
		STATIC_VAR(hist) = calloc(pts, sizeof(double));
		STATIC_VAR(hist_t) = calloc(pts, sizeof(double));
		STATIC_VAR(prox_t) = calloc(1, sizeof(double));
		STATIC_VAR(saida) = calloc(1, sizeof(double));
		
		pos = STATIC_VAR(pos);
		hist = STATIC_VAR(hist);
		hist_t = STATIC_VAR(hist_t);
		prox_t = STATIC_VAR(prox_t);
		saida = STATIC_VAR(saida);
		*saida = 0.0;  //inicia a saida em zero, ate o calculo do historico
		// se houver erro, envia mensagem para terminal
		if ((pos == NULL) || (hist == NULL) || (hist_t == NULL) || (prox_t == NULL) || (saida == NULL))
			cm_message_send(alloc_error_rms);
	}
	else {
		pos = STATIC_VAR(pos);
		hist = STATIC_VAR(hist);
		hist_t = STATIC_VAR(hist_t);
		prox_t = STATIC_VAR(prox_t);
		saida = STATIC_VAR(saida);
	}
	
	//------------------ Rotina de  amostragem ------------------
	if(TIME == 0.0) { //se eh o primeiro
		*prox_t = passo; 	// define o proximo tempo
		hist[*pos] = INPUT(in) * INPUT(in); //coloca o dado de (entrada)^2 no historico
		hist_t[*pos] = TIME; //coloca o tempo no historico
		*pos = *pos + 1; // passa para o proximo item do buffer
		if (*pos >= pts) { *pos = 0;} // buffer circular
	}
	else {
		// verifica se o tempo atual eh o tempo agendado
		if (TIME >= *prox_t){
			*prox_t = TIME + passo; 	// define o proximo tempo
			
			hist[*pos] = INPUT(in) * INPUT(in); //coloca o dado de (entrada)^2 no historico
			hist_t[*pos] = TIME; //coloca o tempo no historico
			*pos = *pos + 1; // passa para o proximo item do buffer
			if (*pos >= pts) { *pos = 0;} // buffer circular
			
			//----------- calcula o Valor RMS da janela de historico ----------
			total = 0.0; //inicializa o acumulador para o laco for
			total_t = 0.0; //inicializa o acumulador para o laco for
			// totaliza o historico dos dados de entrada
			for(i = 1; i < pts; i++) {
				index1 = (i + *pos) % pts;
				index2 = (i + *pos -1) % pts;
				total = total + 0.5*(hist[index1]+hist[index2])*fabs(hist_t[index1]-hist_t[index2]); //integral dos dados de (entrada)^2
				total_t = total_t + fabs(hist_t[index1]-hist_t[index2]); //periodo total da janela
				
				// exemplo de mensagem para o terminal:
				//sprintf(msg, "i=%d v=%4.2f t=%4.2f", i , hist[i], total); //retirar
				//cm_message_send(msg);
			}
			if (total_t != 0) *saida = sqrt(total / total_t); //calcula o valor RMS final
		}
	} //------------------------------------------------------------------
	
	OUTPUT(out) = *saida;	//saida via variavel de retensao
	PARTIAL(out,in) = 0.0;
}
