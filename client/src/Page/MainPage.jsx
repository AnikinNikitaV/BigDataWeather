import React, {useState} from 'react';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';
import {optionsCity, optionsTask} from './config';
import styles from './MainPage.scss';
import InputLabel from '@mui/material/InputLabel';
import FormControl from '@mui/material/FormControl';
import NativeSelect from '@mui/material/NativeSelect';
import {range} from './utils';
import axios from 'axios';

const URL = 'http://127.0.0.1:8000';
const DEFAULT_START_YEAR = 1997;
const DEFAULT_END_YEAR = new Date().getFullYear();

const MainPage = () => {
    const [task, setTask] = useState();
    const [city, setCity] = useState();
    const [startYear, setStartYear] = useState(DEFAULT_START_YEAR);
    const [endYear, setEndYear] = useState(DEFAULT_END_YEAR);
    const [url, setUrl] = useState();

    const years = range(DEFAULT_START_YEAR, DEFAULT_END_YEAR);

    const displaySelect = (name, handler, defaultValue) => <FormControl fullWidth>
        <InputLabel variant="standard" htmlFor="uncontrolled-native">
            {name}
        </InputLabel>
        <NativeSelect
            defaultValue={defaultValue.toString()}
            onChange={(e) => handler(e.target.value)}
        >
            {years.map(year => <option key={year} value={year}>{year}</option>)}
        </NativeSelect>
    </FormControl>

    const searchHandler = () => {
        console.log(task, city, startYear, endYear);
        const urlToServer = `${URL}/api/?task=${task}&city=${city}&startYear=${startYear}&endYear=${endYear}`;
        axios.get(urlToServer)
            .then(response => {
            console.log(response.data);
            setUrl(response.data);
        });
    }


    return (
        <div className="container">
            <div className="item-autocomplete">
                <Autocomplete
                    disablePortal
                    id="combo-box-demo"
                    options={optionsTask}
                    onChange={(e, value) => {
                        setTask(value.id);
                    }}
                    value={task}
                    renderInput={(params) =>
                        <TextField {...params}
                                   variant="standard"
                                   size="small"
                                   label="Выберите задачу"
                        />}
                />
            </div>
            <Autocomplete
                disablePortal
                id="combo-box-demo"
                options={optionsCity}
                onChange={(e, value) => {
                    setCity(value?.label);
                }}
                value={city}
                inputValue={city}
                renderInput={(params) =>
                    <TextField {...params}
                               variant="standard"
                               size="small"
                               label="Выберите город"
                    />}
            />
            <div className="container-year">
                <div className="item-year">
                    {displaySelect("начальный год", setStartYear, DEFAULT_START_YEAR)}
                </div>
                <div className="item-year">
                    {displaySelect("конечный год", setEndYear, DEFAULT_END_YEAR)}
                </div>
            </div>
            <div className="btn-search">
                <Button variant="contained" onClick={searchHandler}>Поиск</Button>
            {/*    {url && <img*/}
            {/*        src="http://127.0.0.1:8000/media/results/draw_graphic_most_frequent_weather_%D0%90%D0%BB%D1%8C%D0%BC%D0%B5%D1%82%D1%8C%D0%B5%D0%B2%D1%81%D0%BA_1997_2021.png"/>}*/}
            </div>
            {url && url.img_url && url.img_url.map((url) =>
                <div className="img-container">
                    <img src={`${URL}/media/${url}.png`} key={url}/>
                </div>
            )}
        </div>
    )
}

export default MainPage