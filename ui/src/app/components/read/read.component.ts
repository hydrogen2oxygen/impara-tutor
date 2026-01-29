import {Component, OnInit} from '@angular/core';
import {OllamaService} from "../../services/ollama.service";
import {FormControl, ReactiveFormsModule} from "@angular/forms";
import {NgIf} from "@angular/common";

@Component({
  selector: 'app-read',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    NgIf
  ],
  templateUrl: './read.component.html',
  styleUrl: './read.component.scss'
})
export class ReadComponent implements OnInit {
  importText = new FormControl('', { nonNullable: true })
  text = new FormControl('', { nonNullable: true })
  responseText = ""
  loading: boolean = false;

  constructor(private ollama:OllamaService ) {}

  ngOnInit(): void {
    this.importText.setValue("Утром я готовлю завтрак.\n" +
      "Я беру яйца и готовлю яичницу.\n" +
      "Яйца жарятся быстро и вкусно пахнут.\n" +
      "Потом я делаю кофе.\n" +
      "Кофе горячий и ароматный.\n" +
      "Я сажусь за стол и ем завтрак.\n" +
      "Завтрак с яйцами и кофе очень вкусный.\n" +
      "Так приятно начинать утро с хорошего завтрака.")
  }


  saveText() {
    console.log("saveText: " + this.importText.value);
    this.text.setValue(this.importText.value);
  }

  testOllama() {
    this.loading = true;

    let question = `Take from this text the most important words and return it as a comma-separated list (only the most important words and avoid comments and other stuff): \n\n${this.text.value}`;

    this.ollama.chat(question).subscribe(response => {
      console.log("Ollama response: ", response);
      this.responseText = response;
      this.loading = false;
    });
  }
}
