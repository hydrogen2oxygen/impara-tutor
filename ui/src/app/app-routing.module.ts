import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {DashboardComponent} from "./components/dashboard/dashboard.component";
import {StatisticsComponent} from "./components/statistics/statistics.component";

const routes: Routes = [
  {path: '', redirectTo: 'HOME', pathMatch: 'full'},
  {path: 'HOME', component: DashboardComponent},
  {path: 'STATISTICS', component: StatisticsComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
