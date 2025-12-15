// Copyright 2025 Charles Bouquet

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import logo from './logo.svg';
import './App.css';
import './tailwind.css'
import { UploadForm } from './preprocessing/DropFile';
function App() {
  return (
    <div className="App">
      <header className="App-header">
        <UploadForm></UploadForm>
        
      </header>
    </div>
  );
}


{/* exemple utilisation Dropzone 
  import Dropzone from 'react-dropzone'

  <Dropzone
        onDrop={acceptedFiles => sendFile(acceptedFiles[0])}
        multiple={false}
        accept={{ 'text/csv': ['.csv'] }}
      >
        {({ getRootProps, getInputProps }) => (
          <section>
            <div
              {...getRootProps()}
              className="cursor-pointer border-2 border-dashed border-gray-300 rounded-md p-8 flex flex-col items-center justify-center hover:border-indigo-500 transition-colors"
            >
              <input {...getInputProps()} />
              <p className="text-gray-500 text-center text-sm">
                Glissez-déposez le fichier ici ou cliquez pour choisir un fichier
              </p>
            </div>
          </section>
        )}
      </Dropzone>
      
      exemple utilisation datepicker:
      import DatePicker from "react-datepicker";
      
      <DatePicker selected={date}
            onChange={(date)=>setDate(date)}
            showMonthYearPicker OU showYearPicker OU RIEN (ça laisse jour, mois, année au choix)
            dateFormat="yyyy"
            placeholderText='Choisir une année'
            className="mt-4 w-48 px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-700"

  />
      */}
export default App;
