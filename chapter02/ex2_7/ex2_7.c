#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "wave.h"
#include "fft.h"

int main(void)
{
  MONO_PCM pcm0;
  int n, k, N;
  double *x_real, *x_imag;
  
  mono_wave_read(&pcm0, "ex2_1.wav"); /* WAVEファイルからモノラルの音データを入力する */
  
  N = 64;
  x_real = calloc(N, sizeof(double)); /* メモリの確保 */
  x_imag = calloc(N, sizeof(double)); /* メモリの確保 */
  
  for (n = 0; n < N; n++)
  {
    x_real[n] = pcm0.s[n]; /* x(n)の実数部 */
    x_imag[n] = 0.0; /* x(n)の虚数部 */
  }
  
  FFT(x_real, x_imag, N); /* FFTの計算結果はx_realとx_imagに上書きされる */
  
  /* 周波数特性 */
  for (k = 0; k < N; k++)
  {
    printf("%d %f+j%f\n", k, x_real[k], x_imag[k]);
  }
  
  free(pcm0.s); /* メモリの解放 */
  free(x_real); /* メモリの解放 */
  free(x_imag); /* メモリの解放 */
  
  return 0;
}
