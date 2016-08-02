/*==================================================
Converte sinais no dominio do tempo para representacao fasorial, via
transformada discreta de fourrier (DFT) na frequencia fundamental.

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

char *alloc_error_phasor = "\n**** Error ****\nPHASOR: Error allocating block storage \n";
#define M_PI 3.14159265358979323846


/*=== MACROS ===========================*/


/*=== LOCAL VARIABLES & TYPEDEFS =======*/


/*=== FUNCTION PROTOTYPE DEFINITIONS ===*/


/*=== Rotina Principal ===*/

void
cm_phasor(ARGS)
{
	int erro;		//flag indicador de erro
	int i;			// iterador 1
	int j;			// iterador 2
	//int index1;	// iterador para buffer circular
	int pts;		// quantidade de pontos para a janela de aquisicao
	int *pos;		// posicao no buffer circular
	double **hist;	// array de buffers circulares, historicos das entradas
	double *prox_t;	// proximo valor de tempo para amostragem
	double passo;		//passo temporal de amostragem
	double out_1;	// acumulador para calculo da componente real
	double out_2;	// acumulador para calculo da componete imaginaria
	double *saida_1; // calculo e retensao da componente real
	double *saida_2; // calculo e retensao da componete imaginaria
	double modulo;
	double angulo;
	int size;		// tamanho do vetor de entradas
	//char msg[40]; 	// string para envio de mensagens

	pts = PARAM(pontos);	//pega a quant de pontos passada
	passo = (double)1/(PARAM(freq)*pts);	//calcula o passo temporal
	size = PORT_SIZE(in); //tamanho do vetor de entradas

	if (INIT == 1) {	//primeira chamada do modulo
		erro = 0;
		// aloca e inicializa a memoria das variaveis
		STATIC_VAR(pos) = calloc(1, sizeof(int));
		STATIC_VAR(prox_t) = calloc(1, sizeof(double));
		STATIC_VAR(saida_1) = calloc(size, sizeof(double));
		STATIC_VAR(saida_2) = calloc(size, sizeof(double));
		STATIC_VAR(hist) = calloc(size, sizeof(double *)); 
		
		pos = STATIC_VAR(pos);		
		prox_t = STATIC_VAR(prox_t);
		saida_1 = STATIC_VAR(saida_1);
		saida_2 = STATIC_VAR(saida_2);
		hist = STATIC_VAR(hist);
		
		if ((pos == NULL) || (prox_t == NULL) || (saida_1 == NULL) ||
				(saida_2 == NULL) || (hist == NULL))
			{ erro = 1; }
		
		for (i=0; i<size; i++) { //aloca um buffer para cada entrada
			hist[i] = calloc(pts, sizeof(double));
			if (hist[i] == NULL) { erro = 1; }
		}
		
		// se houver erro na alocacao, envia mensagem para terminal
		if (erro) { cm_message_send(alloc_error_phasor); }
	}
	else {
		pos = STATIC_VAR(pos);		
		prox_t = STATIC_VAR(prox_t);
		saida_1 = STATIC_VAR(saida_1);
		saida_2 = STATIC_VAR(saida_2);
		hist = STATIC_VAR(hist);
	}
	
	//------------------ Rotina de  amostragem ------------------
	if(TIME == 0.0) { //se eh o primeiro
		*prox_t = passo; 	// define o proximo tempo
		for (i=0; i<size; i++) {
			hist[i][*pos] = INPUT(in[i]); //coloca o dado de entrada[i] no historico correspondente
		}
		*pos = *pos + 1; // passa para o proximo item do buffer
		if (*pos >= pts) { *pos = 0;} // buffer circular
	}
	else {
		// verifica se o tempo atual eh o tempo agendado
		if (TIME >= *prox_t){
			*prox_t = TIME + passo; 	// define o proximo tempo
			for (i=0; i<size; i++) {
				hist[i][*pos] = INPUT(in[i]); //coloca o dado de entrada[i] no historico
			}
			*pos = *pos + 1; // passa para o proximo item do buffer
			if (*pos >= pts) { *pos = 0;} // buffer circular
			
			//----------- calcula a DFT da janela de historico ----------
			for (i=0; i<size; i++) { //para cada entrada
				out_1 = 0.0; //inicializa o acumulador para o laco for
				out_2 = 0.0; //inicializa o acumulador para o laco for
				// totaliza cada componente
				for(j = 0; j < pts; j ++) {
					//index1 = (j + *pos) % pts;
					//calcula componente real
					out_1 = out_1 + (hist[i][j] * cos(2 * M_PI * j / pts));
					//calcula componente imaginaria
					out_2 = out_2 - (hist[i][j] * sin(2 * M_PI * j / pts));
					
					// exemplo de mensagem para o terminal:
					//sprintf(msg, "i=%d v=%4.2f t=%4.2f", i , hist[i], total); //retirar
					//cm_message_send(msg);
				}
				saida_1[i] = 2 * out_1/pts; //variavel de retencao parte real
				saida_2[i] = 2 * out_2/pts; //variavel de retencao parte imaginaria
				if (!(PARAM(r_p))) { // se for requisitado saida polar
					modulo = sqrt(pow(saida_1[i],2)+pow(saida_2[i],2));
					angulo = atan2(saida_2[i],saida_1[i]);
					saida_1[i] = modulo;
					saida_2[i] = angulo;
				}
			}
		}
	} //------------------------------------------------------------------
	for (i=0; i<size; i++) { //para cada entrada, duas saidas correspondentes
		OUTPUT(out_1[i]) = saida_1[i];	//saida via variavel de retensao real
		OUTPUT(out_2[i]) = saida_2[i];	//saida via variavel de retensao imag
	}
	/*PARTIAL(out_p,in_i) = 0.0;
	PARTIAL(out_q,in_i) = 0.0;
	PARTIAL(out_p,in_v) = 0.0;
	PARTIAL(out_q,in_v) = 0.0;*/
}
