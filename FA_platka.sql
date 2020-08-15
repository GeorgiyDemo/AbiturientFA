-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Хост: database:3306
-- Время создания: Авг 15 2020 г., 10:57
-- Версия сервера: 5.7.31
-- Версия PHP: 7.4.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `FA_platka`
--

-- --------------------------------------------------------

--
-- Структура таблицы `buf_table`
--

CREATE TABLE `buf_table` (
  `id` int(11) NOT NULL,
  `profile_link` varchar(45) NOT NULL,
  `first_name` varchar(45) NOT NULL,
  `last_name` varchar(45) NOT NULL,
  `club_link` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Структура таблицы `table_updates`
--

CREATE TABLE `table_updates` (
  `id` int(11) NOT NULL,
  `number` varchar(455) NOT NULL,
  `fio` varchar(455) NOT NULL,
  `contesttype` varchar(455) NOT NULL,
  `score` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Структура таблицы `vk_users`
--

CREATE TABLE `vk_users` (
  `id` int(11) NOT NULL,
  `first_name` varchar(455) NOT NULL,
  `last_name` varchar(455) NOT NULL,
  `link` varchar(455) NOT NULL,
  `full_name` varchar(455) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `buf_table`
--
ALTER TABLE `buf_table`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `profile_link_UNIQUE` (`profile_link`);

--
-- Индексы таблицы `table_updates`
--
ALTER TABLE `table_updates`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `number_UNIQUE` (`number`),
  ADD UNIQUE KEY `id_UNIQUE` (`id`);

--
-- Индексы таблицы `vk_users`
--
ALTER TABLE `vk_users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `link_UNIQUE` (`link`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `buf_table`
--
ALTER TABLE `buf_table`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=100331;

--
-- AUTO_INCREMENT для таблицы `table_updates`
--
ALTER TABLE `table_updates`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11384;

--
-- AUTO_INCREMENT для таблицы `vk_users`
--
ALTER TABLE `vk_users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=259;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
