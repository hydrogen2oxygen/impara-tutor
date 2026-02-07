import { Component } from '@angular/core';
import {User} from "../../domains/User";
import {FormControl} from "@angular/forms";

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent {
  user: User | undefined
  display_name: FormControl = new FormControl('', { nonNullable: true })
  email: FormControl = new FormControl('', { nonNullable: true })
  bio: FormControl = new FormControl('', { nonNullable: true })

  register() {
    this.user = new User()
    this.user.display_name = this.display_name.getRawValue()
    this.user.bio = this.bio.getRawValue()
    this.user.email = this.email.getRawValue()
    this.user.created_at = new Date()
    this.user.last_active_at = new Date()
    console.log(this.user)
  }
}
