import {Component, OnInit} from '@angular/core';
import {User} from "../../domains/User";
import {FormControl} from "@angular/forms";
import {ImparaService} from "../../services/impara.service";

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {

  user: User | null = null // synchronized with ImparaService.user$
  userList: User[] = []
  display_name: FormControl = new FormControl('', {nonNullable: true})
  email: FormControl = new FormControl('', {nonNullable: true})
  bio: FormControl = new FormControl('', {nonNullable: true})

  constructor(private imparaService: ImparaService) {
  }

  ngOnInit(): void {
    let currentUser = localStorage.getItem("currentUser")
    if (currentUser) {
      this.user = JSON.parse(currentUser)
    } else {
      this.imparaService.listUsers().subscribe( users => { this.userList = users })
    }
    this.imparaService.user$.subscribe( user => {this.user = user})
  }

  register() {
    this.user = new User()
    this.user.display_name = this.display_name.getRawValue()
    this.user.bio = this.bio.getRawValue()
    this.user.email = this.email.getRawValue()
    this.user.created_at = new Date()
    this.user.last_active_at = new Date()
    this.imparaService.createUser(this.user).subscribe(user => {
      this.imparaService.setUser(user)
    })
  }

  selectUser(user: User) {
    this.imparaService.setUser(user)
  }
}
