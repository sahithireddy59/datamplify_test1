import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-easy-connect',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './easy-connect.component.html',
  styleUrl: './easy-connect.component.scss'
})
export class EasyConnectComponent {
  connections = [
    { id: 1, name: 'Snowflake Analytics', type: 'Database', status: 'Active' },
    { id: 2, name: 'Customer CSV Upload', type: 'File', status: 'Inactive' },
    { id: 3, name: 'Salesforce Integration', type: 'Integration', status: 'Active' }
  ];

  connectionTypes = ['Database', 'File', 'Integration'];

  selectedConnectionType: string | null = null;
  isAddingConnection = false;

  toggleAddConnection() {
    this.isAddingConnection = !this.isAddingConnection;
    this.selectedConnectionType = null;
  }

  selectType(type: string) {
    this.selectedConnectionType = type;
  }

  addConnection() {
    alert(`New ${this.selectedConnectionType} connection created!`);
    this.isAddingConnection = false;
  }
}
