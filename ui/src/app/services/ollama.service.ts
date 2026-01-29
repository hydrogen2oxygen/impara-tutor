import { Injectable } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {firstValueFrom, map, Observable} from 'rxjs';

type OllamaChatResponse = {
  message?: { role: string; content: string };
  done?: boolean;
};

@Injectable({
  providedIn: 'root'
})
export class OllamaService {

  private baseUrl = 'http://localhost:11434';
  private baseModel = 'qwen3-vl:8b';

  constructor(private http: HttpClient) {}

  chat(question: string): Observable<string> {
    console.log(question)
    const body = {
      model: this.baseModel,
      stream: false,
      messages: [
        {
          role: 'user',
          content:`${question}`
        }
      ]
    };

    return this.http
      .post<OllamaChatResponse>(`${this.baseUrl}/api/chat`, body)
      .pipe(
        map(res => res?.message?.content ?? '')
      );
  }
}
