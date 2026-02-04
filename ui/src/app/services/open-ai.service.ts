import {Injectable} from '@angular/core';
import {environment} from "../../environments/environment";
import {HttpClient} from "@angular/common/http";
import {Observable} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class OpenAiService {

  baseUrl: string = environment.baseUrl

  constructor(private http: HttpClient) {
  }

  chat(model: string, question: string, system: string): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}openAi`, {
      model: model,
      system: system,
      prompt: question
    });
  }
}
