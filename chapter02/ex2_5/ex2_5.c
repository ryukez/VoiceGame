#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "wave.h"

int main(void)
{
  MONO_PCM pcm1;
  int n, i;
  double A, f0;
  
  pcm1.fs = 8000; /* 標本化周波数 */
  pcm1.bits = 16; /* 量子化精度 */
  pcm1.length = 8000; /* 音データの長さ */
  pcm1.s = calloc(pcm1.length, sizeof(double)); /* メモリの確保 */
  
  A = 0.25; /* 振幅 */
  f0 = 250.0; /* 基本周波数 */
  
  /* コサイン波のノコギリ波 */
  for (n = 0; n < pcm1.length; n++)
  {
    for (i = 1; i <= 15; i++) /* 15倍音までの重ね合わせ */
    {
      pcm1.s[n] += A / i * cos(2.0 * M_PI * f0 * i * n / pcm1.fs);
    }
  }
  
  mono_wave_write(&pcm1, "ex2_5.wav"); /* WAVEファイルにモノラルの音データを出力する */
  
  free(pcm1.s); /* メモリの解放 */
  
  return 0;
}
