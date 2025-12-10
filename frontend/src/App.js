import logo from './logo.svg';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
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
