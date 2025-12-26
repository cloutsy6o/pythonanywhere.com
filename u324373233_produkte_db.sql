-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Nov 21, 2025 at 11:44 AM
-- Server version: 11.8.3-MariaDB-log
-- PHP Version: 7.2.34

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `u324373233_produkte_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `preis_historie`
--

CREATE TABLE `preis_historie` (
  `id` int(11) NOT NULL,
  `produkt_id` int(11) NOT NULL,
  `preis` decimal(10,2) NOT NULL,
  `geprueft_am` datetime DEFAULT current_timestamp(),
  `shop_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `preis_historie`
--

INSERT INTO `preis_historie` (`id`, `produkt_id`, `preis`, `geprueft_am`, `shop_id`) VALUES
(14, 3, 3.85, '2025-08-16 14:29:43', 3),
(15, 3, 3.27, '2025-08-16 14:39:17', 3),
(16, 3, 3.27, '2025-08-17 23:24:58', 3),
(17, 3, 3.15, '2025-08-18 11:50:53', 3),
(18, 3, 3.15, '2025-08-19 10:54:05', 3),
(19, 3, 3.15, '2025-08-19 23:11:55', 3),
(20, 3, 2.70, '2025-08-21 13:57:49', 3),
(21, 3, 3.18, '2025-08-21 14:06:56', 3),
(22, 3, 3.18, '2025-08-21 20:17:04', 3),
(23, 3, 3.18, '2025-08-22 02:45:36', 3),
(24, 3, 3.17, '2025-08-25 17:37:35', 3);

-- --------------------------------------------------------

--
-- Table structure for table `produkte`
--

CREATE TABLE `produkte` (
  `id` int(11) NOT NULL,
  `titel` varchar(255) NOT NULL,
  `beschreibung` text DEFAULT NULL,
  `bild` varchar(255) DEFAULT NULL,
  `label` varchar(50) DEFAULT NULL,
  `erstellt_am` datetime DEFAULT current_timestamp(),
  `bewertung_durchschnitt` decimal(2,1) NOT NULL,
  `bewertung_anzahl` int(11) NOT NULL,
  `aliexpress_product_id` bigint(20) DEFAULT NULL,
  `current_price` decimal(10,2) NOT NULL DEFAULT 0.00,
  `last_checked` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `produkte`
--

INSERT INTO `produkte` (`id`, `titel`, `beschreibung`, `bild`, `label`, `erstellt_am`, `bewertung_durchschnitt`, `bewertung_anzahl`, `aliexpress_product_id`, `current_price`, `last_checked`) VALUES
(3, 'Lückenreinigungsbürste', 'küche badezimmer Groove Gap Cleaning Brushelektrische reinigungsbürste,Premium schrubber mit Aluminiumstütze mit 15°-Winkel Zauberbürste, dünne Reinigungsbürste für die Küche', 'uploads/lueckenreinigungsbuersten.jpg', 'Bestseller', '2025-08-03 08:47:56', 4.3, 4664, NULL, 0.00, '2025-08-15 13:06:21'),
(6, 'Nähset mit Nähzubehör', 'Spulen Faden, Großformat Premium Näh, komplettes Nähzeug für Anfänger,Reisende, Verwandte und Freunde', 'uploads/bild_689c711bb756d1.42990557.jpg', 'Bestseller', '2025-08-13 11:03:55', 4.5, 30918, NULL, 0.00, '2025-08-15 13:06:21'),
(7, 'Umisleep Schlafmaske für Seitenschläfer', '3D-Augenhöhlen und verstellbares Gummiband, lichtblockierend und atmungsaktiv, Augenmaske für Männer und Frauen, geeignet für Reise-Yoga, Schwarz', 'uploads/bild_689c75725bc474.16069331.jpg', '', '2025-08-13 11:22:26', 4.6, 1666, NULL, 0.00, '2025-08-15 13:06:21'),
(8, 'LARS NYSØM Salz und Pfeffer Mühle', '2er Set Manuell mit einstellbarem Keramik-Mahlwerk von grob bis fein I Design Gewürzmühlenset (2 Stück) (Carbon Black)', 'uploads/bild_689c89c593dca8.04242815.jpg', '', '2025-08-13 12:49:09', 4.5, 6631, NULL, 0.00, '2025-08-15 13:06:21'),
(9, 'Hekatron Genius Plus', '– Rauchmelder 10 Jahre Batterie – Testsieger Stiftung Warentest – Made in Germany – inkl. 1x Klebepad – App-unterstützt – Feuermelder – mehrsprachig – 1 Stück', 'uploads/bild_689c8bc1b3b6e4.52061278.jpg', '', '2025-08-13 12:57:37', 4.4, 4365, NULL, 0.00, '2025-08-15 13:06:21'),
(10, '2 Stück Abflusssieb Silikon', 'Abflusssieb Dusche Haarfänger Badewanne Abflussabdeckung, Abflusssieb für Badezimmer Badewanne und Küche (2 Grau)\r\nMarke: CCLKHY', 'uploads/abflusssieb.jpeg', 'Bestseller', '2025-08-13 13:08:25', 4.0, 6924, NULL, 0.00, '2025-08-15 13:06:21'),
(11, 'TrendPlain 16oz Ölsprüher für Speiseöl', '– 470ml Olivenöl Flasche – 2-in-1 Ölspender und Ölsprüher – Küchen Gadgets für Kochen, Salat und Grill Schwarz', 'uploads/bild_689c9070c780d4.85726365.jpg', 'Bestseller', '2025-08-13 13:17:36', 4.4, 24306, NULL, 0.00, '2025-08-15 13:06:21'),
(12, 'tesa Insect Stop Standard Fliegengitter für Fenster', ' - Insektenschutz zuschneidbar - Mückenschutz ohne Bohren - 1 x Fliegen Netz - 130 cm x 150 cm', 'uploads/bild_689c944125cd29.15748906.jpg', 'Bestseller', '2025-08-13 13:33:53', 4.4, 38509, NULL, 0.00, '2025-08-15 13:06:21'),
(13, 'STAEDTLER Buntstifte Kinder Set Noris Colour', ' – Bruchsicherer Buntstift mit ergonomischer Dreikantform – Farbstifte mit rutschfester Soft-Oberfläche – 16er Pack mit brillanten Farben', 'uploads/bild_689c9610c1e582.18335062.jpg', '', '2025-08-13 13:41:36', 4.7, 11080, NULL, 0.00, '2025-08-15 13:06:21'),
(14, 'Leifheit Standtrockner Pegasus 180 Solid', 'Wäscheständer mit Flügeln für Lange Kleidungsstücke, standfester Flügelwäschetrockner für drinnen und draußen, 18m Trockenlänge', 'uploads/bild_689c97583b8065.57689000.jpg', 'Bestseller', '2025-08-13 13:47:04', 4.6, 8413, NULL, 0.00, '2025-08-15 13:06:21'),
(15, 'Vileda ULTRAMAX 2in1 Bodenwischer Komplett-Set', '| Mopp mit Mikrofaserbezug & Eimer mit Auswringfunktion | Hygienisches Bodenreinigungssystem für Parkett, Laminat & Fliesen', 'uploads/bild_689c98b06f2355.96014605.jpg', '', '2025-08-13 13:52:48', 4.4, 7302, NULL, 0.00, '2025-08-15 13:06:21'),
(18, 'Schaber Set', 'Kochfeldschaber, Glasschaber, 20 Ersatzklingen, Küchenschaber, Reinigungsschaber, stabiler Schaber, Backofenschaber, Kleberentferner', 'uploads/bild_68aed850f05366.13468990.jpeg', NULL, '2025-08-27 10:05:04', 4.6, 2025, NULL, 0.00, '2025-08-27 10:05:04'),
(19, 'Gläser Untersetzer Filz', '12er Set mit Halter, rund, 10cm Durchmesser, Bierdeckel, Restaurant, Büro, Bar, Getränke', 'uploads/bild_68aee55806d394.35678315.jpeg', NULL, '2025-08-27 11:00:40', 4.7, 3809, NULL, 0.00, '2025-08-27 11:00:40'),
(20, 'Reinigungsbürste für Abwasserkanäle', '2 Stück, Rohrreiniger, Abwasserbürste, Haar Entferner, Lange Haare, 45cm lang, flexible, Küche, Badezimmer', 'uploads/bild_68aeed9aeb3aa1.69168222.jpeg', NULL, '2025-08-27 11:35:54', 4.0, 1373, NULL, 0.00, '2025-08-27 11:35:54'),
(21, 'Bürste für Haustiere', 'Hunde, Katze, Kurzhaar, Langhaar, Hundebürste, Katzenbürste, mit Knopf', 'uploads/bild_68af24b4d8d9e8.15991159.jpeg', NULL, '2025-08-27 15:31:00', 4.3, 34003, NULL, 0.00, '2025-08-27 15:31:00'),
(22, 'Sicherheitsgurt für Haustiere', '1 Stück, schwarz, Auto, einstellbar, Universalstecker, Hunde, Hundegurt', 'uploads/bild_68af2cf72ceb99.25193258.jpeg', NULL, '2025-08-27 16:06:15', 4.6, 5754, NULL, 0.00, '2025-08-27 16:06:15'),
(24, 'Tierhaarentferner', 'Fusselrolle, Hundehaare, Katzenhaare, Tierhaare, für Sofa, Bett, Teppich, Kratzbaum, wiederverwendbar,  ', 'uploads/bild_68b1cb5db5bff7.90545902.jpeg', NULL, '2025-08-29 15:46:37', 4.3, 95142, NULL, 0.00, '2025-08-29 15:46:37'),
(25, 'Edelstahl Handtuchhalter', '6 Stück, ohne Bohren, schwarz, Edelstahl, wasserfest, selbstklebend, Handtuchhaken, Badezimmer, Toilette, Küche, Büro', 'uploads/bild_68b1d09dd88476.17200505.jpeg', NULL, '2025-08-29 16:09:01', 4.6, 4957, NULL, 0.00, '2025-08-29 16:09:01'),
(26, 'WATERPROOF Fahrradabdeckung', 'wasserdicht, Allwetter, schwarz, verstärkte Nähte, Fahrradgarage, draussen, Fahrradhülle, Windschutz', 'uploads/bild_68b5aebd393dd4.19926983.jpeg', NULL, '2025-09-01 14:33:33', 4.3, 1213, NULL, 0.00, '2025-09-01 14:33:33'),
(27, 'Fahrradklingel', 'Geheimfach für Apple AirTag, Diebstahltschutz, Diebstahlsicherung, Fahrrad, ', 'uploads/bild_68b5b85f0dafd0.13015392.jpeg', NULL, '2025-09-01 15:14:39', 4.5, 4079, NULL, 0.00, '2025-09-01 15:14:39'),
(28, 'Handyhalterung', 'verstellbar, faltbar, stabil, geeignet für iPhone 16/15/14/13/12/11 Pro, XS Max, Nintendo Switch und alle Smartphones', 'uploads/bild_68cd83f441a330.22106124.jpeg', NULL, '2025-09-19 16:25:24', 4.7, 65093, NULL, 0.00, '2025-09-19 16:25:24'),
(29, 'Joyroom Kabelhalter', '6 Stück, magnetischer Kabelhalter, Kabelclips, Kalbelbinder, selbstklebend', 'uploads/bild_68ce7ecfdb8a03.93849917.jpeg', NULL, '2025-09-20 10:15:43', 4.6, 3123, NULL, 0.00, '2025-09-20 10:15:43'),
(30, 'Kabelhalter ', 'Kabelclips, Kabelklemmen, magnetisch, selbstklebend', 'uploads/bild_68cea9a72db3b5.59466424.jpeg', NULL, '2025-09-20 13:18:31', 4.2, 42, NULL, 0.00, '2025-09-20 13:18:31'),
(31, 'Haustierpflegehandschuh', 'Fellpflegehandschuh, sanft, für Hund, Katze, Pferde, langes Fell, Bürsten für Haustiere, Silikonmaterial', 'uploads/bild_68ceee2c17dcc7.45741209.jpeg', NULL, '2025-09-20 18:10:52', 4.0, 2741, NULL, 0.00, '2025-09-20 18:10:52'),
(32, 'Handyband', 'universal, Kette, mit jeder Handy/Smartphone oder Hülle kompatibel', 'uploads/bild_68cef2cadfdd52.55179734.jpeg', NULL, '2025-09-20 18:30:34', 4.4, 4451, NULL, 0.00, '2025-09-20 18:30:34'),
(33, 'Handyband', 'universal, Kette, mit jeder Handy/Smartphone oder Hülle kompatibel', 'uploads/bild_68d127c5c18b84.25287455.jpeg', NULL, '2025-09-22 10:41:09', 4.4, 4451, NULL, 0.00, '2025-09-22 10:41:09'),
(34, 'HAISSKY Sportarmband mit Kopfhörer Tasche', 'Sport Handyhülle für iPhone 16 Pro Max/ 15 Pro/14/13 Pro/12 Plus, Huawei P70 Pro/P60 Pro/Mate 60 Xiaomi, Galaxy, Running, Laufen, Joggen', 'uploads/bild_68d133e4975229.10495529.jpeg', NULL, '2025-09-22 11:32:52', 4.2, 10360, NULL, 0.00, '2025-09-22 11:32:52'),
(35, 'DUNSOO Fitness Handtuch', '120 x 50 cm, Mikrofaser, Sport, Gym Handtuch mit Reißverschluss-Tasche, für Fitness und Training, ', 'uploads/bild_68d13882a1b4e4.23727386.jpeg', NULL, '2025-09-22 11:52:34', 4.4, 1009, NULL, 0.00, '2025-09-22 11:52:34'),
(36, 'Handtrainer / Unterarmtrainer', 'schwarz, verstellbarer Widerstand 5 bis 60 kg, Griffkraft, rutschfester Griff, Stärketrainer, Unterarmstärker für Muskelaufbau & Verletzungsrehabilitation ', 'uploads/bild_68d146d9bc64a2.32691982.jpeg', NULL, '2025-09-22 12:53:45', 4.3, 1468, NULL, 0.00, '2025-09-22 12:53:45'),
(37, 'Kabel Organizer für elektronisches Zubehör', '19 x 11 x 5.5 cm, schwarz, robustes Polyester, mehrere Fächer für Datenkabel, Ladegeräte, Bürobedarf und Elektronikzubehör, Kabeltasche', 'uploads/bild_68d15a96876fb9.30769188.jpeg', NULL, '2025-09-22 14:17:58', 4.4, 864, NULL, 0.00, '2025-09-22 14:17:58');

-- --------------------------------------------------------

--
-- Table structure for table `produkt_preise`
--

CREATE TABLE `produkt_preise` (
  `id` int(11) NOT NULL,
  `produkt_id` int(11) NOT NULL,
  `shop_id` int(11) NOT NULL,
  `link` varchar(500) DEFAULT NULL,
  `aliexpress_id` bigint(20) DEFAULT NULL,
  `aktueller_preis` decimal(10,2) NOT NULL DEFAULT 0.00,
  `letzte_pruefung` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `produkt_preise`
--

INSERT INTO `produkt_preise` (`id`, `produkt_id`, `shop_id`, `link`, `aliexpress_id`, `aktueller_preis`, `letzte_pruefung`) VALUES
(1, 6, 1, 'https://www.otto.de/p/nuodwell-naehkaestchen-naehset-mit-86-naehzubehoer-tragbares-mini-naehset-fuer-anfaenger-reisende-S00B504M/#variationId=S00B504MR6IL', NULL, 12.99, '2025-08-15 13:55:56'),
(2, 6, 2, 'https://amzn.to/4fZeThS', NULL, 5.98, '2025-08-15 13:55:56'),
(3, 6, 3, 'https://s.click.aliexpress.com/e/_onuOk7x', 1005009188914170, 2.89, '2025-08-25 17:37:35'),
(5, 3, 2, 'https://amzn.to/4oIhikP', NULL, 6.99, '2025-08-19 15:22:20'),
(6, 3, 4, 'https://temu.to/k/eb0grbcanlz', NULL, 3.23, '2025-08-19 15:22:20'),
(8, 7, 2, 'https://amzn.to/4fQUMCg', NULL, 5.99, '2025-08-21 19:43:58'),
(9, 7, 1, 'https://www.otto.de/p/heyork-schlafmaske-3d-schlafmaske-augenmaske-atmungsaktiv-fuer-reisen-nickerchen-unisex-S0SC10PY/#variationId=S0SC10PYMEMJ', NULL, 10.95, '2025-08-21 19:46:31'),
(10, 15, 2, 'https://amzn.to/4mSmwJ1', NULL, 21.19, '2025-08-21 19:50:20'),
(11, 15, 1, 'https://www.otto.de/p/vileda-wischmopp-wischer-ultramax-2-in-1-komplettset-bodenwischer-schwarz-rot-CS077J0HI/#variationId=S077J0HI9VUI', NULL, 21.49, '2025-08-21 19:53:03'),
(12, 13, 2, 'https://amzn.to/3HNDOrI', NULL, 3.69, '2025-08-21 19:54:58'),
(13, 13, 1, 'https://www.otto.de/p/staedtler-buntstift-noris-colour-16-tlg-mit-ergonomischer-softoberflaeche-S0E0B0MA/#variationId=S0E0B0MA2W8P', NULL, 3.69, '2025-08-21 19:56:26'),
(14, 12, 2, 'https://amzn.to/4mx3eZW', NULL, 5.85, '2025-08-21 19:57:41'),
(15, 12, 1, 'https://www.otto.de/p/tesa-insektenschutz-fensterrahmen-insect-stop-standard-fliegengitter-fuer-fenster-1-3-m-1-5-m-packung-1-st-fliegennetz-klettband-insektenschutzgitter-fliegenetz-ohne-bohren-zuschneidbar-1960194121/?variationId=1960194300', NULL, 7.75, '2025-08-21 20:00:03'),
(16, 14, 1, 'https://www.otto.de/p/leifheit-waeschestaender-standtrockner-pegasus-180-solid-plus-18m-trockenlaenge-105cm-fluegelhoehe-kleinteilehalter-zusammenklappbar-CS078107H/#variationId=S093Z0P1G1EM', NULL, 37.99, '2025-08-21 20:03:10'),
(17, 14, 2, 'https://amzn.to/3JpBbNr', NULL, 37.99, '2025-08-21 20:03:57'),
(18, 9, 2, 'https://amzn.to/3HKTI6g', NULL, 29.99, '2025-08-21 20:06:26'),
(19, 9, 1, 'https://www.otto.de/p/hekatron-hekatron-genius-plus-mehrsprachig-rauchmelder-S0DDY0L0/#variationId=S0DDY0L0DW9T', NULL, 29.99, '2025-08-21 20:09:50'),
(20, 11, 1, 'https://www.otto.de/p/surfou-oelspender-oelsprueher-2-in-1-oelspruehflasche-oelflasche-olivenoel-spray-470ml-glas-glas-oelspender-mit-sprueh-und-ausgiessfunktion-ideal-fuer-kueche-heissluftfritteuse-salat-bbq-470-ml-bpa-frei-S0NEF0RN/#variationId=S0NEF0RNS9G0', NULL, 10.99, '2025-08-21 20:12:41'),
(21, 11, 2, 'https://amzn.to/4oM3Yfj', NULL, 9.34, '2025-08-21 20:13:13'),
(22, 8, 1, 'https://www.otto.de/p/lars-nysom-gewuerzmuehle-lagom-S0T8K0HN/#variationId=S0T8K0HNPYIS', NULL, 39.99, '2025-08-21 20:14:59'),
(23, 8, 2, 'https://amzn.to/4fOwqZY', NULL, 42.99, '2025-08-21 20:16:32'),
(24, 10, 2, 'https://amzn.to/4lNBrDr', NULL, 4.59, '2025-08-25 18:03:04'),
(25, 10, 4, 'https://app.temu.com/m/nlkte5kdfph', NULL, 1.58, '2025-08-25 19:33:39'),
(32, 18, 2, 'https://amzn.to/3JxKwCL', NULL, 4.79, '2025-08-27 10:05:04'),
(33, 18, 3, 'https://s.click.aliexpress.com/e/_ol9E9sd', 0, 3.35, '2025-08-27 10:05:04'),
(34, 18, 4, 'https://app.temu.com/m/n107a9vr0he', NULL, 1.75, '2025-08-27 10:05:04'),
(35, 19, 2, 'https://amzn.to/4lLQ7Ty', NULL, 9.99, '2025-08-27 11:00:40'),
(36, 19, 4, 'https://temu.to/k/eztt2qla54p', NULL, 3.98, '2025-08-27 11:00:40'),
(37, 20, 2, 'https://amzn.to/4mVM8F9', NULL, 5.29, '2025-08-27 11:35:54'),
(38, 20, 3, 'https://s.click.aliexpress.com/e/_olhx2Rx', 0, 3.12, '2025-08-27 11:35:54'),
(39, 20, 4, 'https://app.temu.com/m/npg320gt9d1', NULL, 1.40, '2025-08-27 11:35:54'),
(40, 21, 2, 'https://amzn.to/3Vk3MpV', NULL, 9.49, '2025-08-27 15:31:00'),
(41, 21, 3, 'https://s.click.aliexpress.com/e/_c4Bp8m4J', 0, 3.27, '2025-08-27 15:31:00'),
(42, 21, 4, 'https://temu.to/k/e0zyffezx6k', NULL, 2.00, '2025-08-27 15:31:00'),
(43, 22, 2, 'https://amzn.to/45VagAG', NULL, 9.99, '2025-08-27 16:06:15'),
(44, 22, 3, 'https://s.click.aliexpress.com/e/_omuHZX3', 0, 4.08, '2025-08-27 16:06:15'),
(47, 24, 2, 'https://amzn.to/3JAZUOZ', NULL, 15.29, '2025-08-29 15:46:37'),
(48, 24, 4, 'https://temu.to/k/emh2ap6omym', NULL, 5.63, '2025-08-29 15:46:37'),
(49, 25, 2, 'https://amzn.to/3HJgE61', NULL, 10.99, '2025-08-29 16:09:01'),
(50, 25, 4, 'https://app.temu.com/m/ncgstra0p7g', NULL, 6.53, '2025-08-29 16:09:01'),
(51, 26, 2, 'https://amzn.to/4oY1WJb', NULL, 11.89, '2025-09-01 14:33:33'),
(52, 26, 3, 'https://s.click.aliexpress.com/e/_olAWnbB', 0, 13.59, '2025-09-01 14:33:33'),
(53, 26, 4, 'https://app.temu.com/m/nx9vcl3xscf', NULL, 10.37, '2025-09-01 14:33:33'),
(54, 27, 2, 'https://amzn.to/461OivU', NULL, 17.90, '2025-09-01 15:14:39'),
(55, 27, 3, 'https://s.click.aliexpress.com/e/_oksQ8pn', 0, 3.55, '2025-09-01 15:14:39'),
(56, 21, 1, 'https://www.otto.de/p/refined-living-fellbuerste-fellbuerste-tierpflege-buerste-selbstreinigend-fellbuerste-buerste-absplusedelstahlplusgummi-selbstreinigend-pflegebuerste-fellbuerste-hundebuerste-katzenbuerste-kurzhaar-langhaar-1-tlg-sanfte-fellpflege-1-tlg-haustierbuerste-mit-automatischer-selbstreinigungsknopf-S0PBI0W5/#variationId=S0PBI0W52YM4', NULL, 9.98, '2025-09-09 09:28:25'),
(58, 27, 1, 'https://www.otto.de/p/airbell-fahrradklingel-fuer-apple-airtag-22-mm-durchmesser-3-tlg-CS0GC8084/#variationId=S0H6904XYH4T', NULL, 19.90, '2025-09-09 09:37:26'),
(59, 24, 1, 'https://www.kaufland.de/product/508530542/?search_value=Tierhaarentferner', NULL, 15.79, '2025-09-09 11:16:26'),
(60, 24, 1, 'https://www.otto.de/p/ace2ace-schutzkragen-tierhaarentferner-fusselrolle-wiederverwendbar-hund-katze-sofa-bett-S0NDJ07M/#variationId=S0NDJ07MGOXB', NULL, 44.95, '2025-09-09 11:26:17'),
(61, 20, 5, 'https://www.kaufland.de/product/502651215/?search_value=Reinigungsb%C3%BCrsten+f%C3%BCr+Abwasserkan%C3%A4le', NULL, 14.99, '2025-09-10 11:44:25'),
(62, 18, 5, 'https://www.kaufland.de/product/493710127/?search_value=kochfeldschaber+20+set', NULL, 13.78, '2025-09-12 10:06:43'),
(63, 6, 5, 'https://www.kaufland.de/product/507616848/?search_value=n%C3%A4hset', 0, 11.95, '2025-09-18 17:53:04'),
(64, 6, 4, 'https://app.temu.com/m/n9p1a5rgg17', NULL, 4.81, '2025-09-19 08:32:02'),
(65, 10, 5, 'https://www.kaufland.de/product/514913238/?search_value=abflusssieb', NULL, 7.85, '2025-09-19 11:05:40'),
(66, 10, 1, 'https://www.otto.de/p/heyork-abflusssieb-2er-abflusssieb-silikon-spuelbecken-sieb-fuer-badezimmer-badewanne-kueche-S02CT0A8/#variationId=S02CT0A88P5C', NULL, 6.85, '2025-09-19 11:07:19'),
(67, 10, 3, 'https://s.click.aliexpress.com/e/_c4nHhf9z', NULL, 2.19, '2025-09-19 11:24:23'),
(68, 28, 1, 'https://www.otto.de/p/blusmart-verstellbarer-handyhalter-smartphone-halterung-bis-8-00-zoll-faltdesign-tragbar-und-tragbar-aus-aluminiumlegierung-robust-und-langlebig-funktioniert-auf-allen-mobiltelefonen-S0FCX0AU/?variationId=S0FCX0AU301K#variationId=S0FCX0AU301K', NULL, 14.69, '2025-09-19 16:25:24'),
(69, 28, 2, 'https://amzn.to/4mtRoiu', NULL, 8.49, '2025-09-19 16:25:24'),
(70, 28, 3, 'https://s.click.aliexpress.com/e/_c2wcCi63', 0, 6.29, '2025-09-19 16:25:24'),
(71, 28, 4, 'https://app.temu.com/m/n4z8d99y2rx', NULL, 4.92, '2025-09-19 16:25:24'),
(72, 29, 2, 'https://amzn.to/4pyy6en', NULL, 8.06, '2025-09-20 10:15:43'),
(73, 29, 3, 'https://s.click.aliexpress.com/e/_c4WmVD9V', 0, 5.29, '2025-09-20 10:15:43'),
(74, 30, 2, 'https://amzn.to/4mtpXoZ', NULL, 4.99, '2025-09-20 13:18:31'),
(75, 30, 3, 'https://s.click.aliexpress.com/e/_c4kO5Js3', 0, 2.05, '2025-09-20 13:18:31'),
(76, 30, 4, 'https://app.temu.com/m/n5du956uerj', NULL, 1.74, '2025-09-20 13:18:31'),
(77, 30, 5, 'https://www.kaufland.de/product/501042720/?search_value=Kabelhalter+6+st%C3%BCck', 0, 16.90, '2025-09-20 13:32:26'),
(78, 29, 5, 'https://www.kaufland.de/product/510095298/?search_value=Kabelhalter+6+st%C3%BCck+joyroom', NULL, 11.79, '2025-09-20 13:35:00'),
(79, 31, 2, 'https://amzn.to/4gyj1Wj', NULL, 5.09, '2025-09-20 18:10:52'),
(80, 31, 4, 'https://app.temu.com/m/na3zi2d37t7', NULL, 2.06, '2025-09-20 18:10:52'),
(81, 32, 2, 'https://amzn.to/46dnfPx', NULL, 6.39, '2025-09-20 18:30:34'),
(82, 32, 4, 'https://www.temu.com/goods.html?refer_share_id=ifYpwoMBt43o193audPjq1st6rCpONoV&refer_share_channel=system_share&_bg_fs=1&share_video=https%3A%2F%2Fgoods-vod.kwcdn.com%2Fgoods-video%2Fd532d616453109418796e718c49090bee0e0a5f8.f30.mp4&from_share=1&share_video_height=720&share_imessage_opt=1&share_img=https%3A%2F%2Fimg.kwcdn.com%2Fproduct%2Ffancy%2Fea56cdef-81c8-47d9-ae7d-36fd44c7c63c.jpg&share_ui_type=1&goods_id=601102340951050&share_video_width=720&_oak_page_source=417&_oak_region=76&refer_share_', NULL, 999.00, '2025-09-20 18:30:34'),
(83, 33, 2, 'https://amzn.to/46dnfPx', NULL, 6.39, '2025-09-22 10:41:09'),
(84, 33, 4, 'https://www.temu.com/goods.html?refer_share_id=ifYpwoMBt43o193audPjq1st6rCpONoV&refer_share_channel=system_share&_bg_fs=1&share_video=https%3A%2F%2Fgoods-vod.kwcdn.com%2Fgoods-video%2Fd532d616453109418796e718c49090bee0e0a5f8.f30.mp4&from_share=1&share_video_height=720&share_imessage_opt=1&share_img=https%3A%2F%2Fimg.kwcdn.com%2Fproduct%2Ffancy%2Fea56cdef-81c8-47d9-ae7d-36fd44c7c63c.jpg&share_ui_type=1&goods_id=601102340951050&share_video_width=720&_oak_page_source=417&_oak_region=76&refer_share_', NULL, 999.00, '2025-09-22 10:41:09'),
(85, 34, 2, 'https://amzn.to/4nJvlW6', NULL, 13.99, '2025-09-22 11:32:52'),
(86, 34, 3, 'https://s.click.aliexpress.com/e/_c4dhPSqL', 0, 4.99, '2025-09-22 11:32:52'),
(87, 34, 4, 'https://app.temu.com/m/nzir86jo6q4', NULL, 3.64, '2025-09-22 11:32:52'),
(88, 35, 2, 'https://amzn.to/4gKneWT', NULL, 12.99, '2025-09-22 11:52:34'),
(89, 35, 4, 'https://app.temu.com/m/n3egxiycype', NULL, 7.00, '2025-09-22 11:52:34'),
(90, 36, 2, 'https://amzn.to/4gKwqKT', NULL, 7.99, '2025-09-22 12:53:45'),
(91, 36, 4, 'https://app.temu.com/m/nojzmmuxww1', NULL, 2.03, '2025-09-22 12:53:45'),
(92, 36, 5, 'https://www.kaufland.de/product/531441484/?search_value=handtrainer', NULL, 6.48, '2025-09-22 13:23:26'),
(93, 36, 1, 'https://www.otto.de/p/emeco-handmuskeltrainer-handtrainer-unterarmtrainer-mit-zaehlfunktion-10-60kg-verstellbarer-fin-S00EH0C8/#variationId=S00EH0C8OA71', NULL, 11.99, '2025-09-22 13:27:51'),
(94, 37, 2, 'https://amzn.to/4pzMYcz', NULL, 14.99, '2025-09-22 14:17:58'),
(95, 37, 3, 'https://s.click.aliexpress.com/e/_c2QLzfF1', 0, 3.49, '2025-09-22 14:17:58'),
(96, 37, 4, 'https://app.temu.com/m/n918befcbn7', NULL, 2.55, '2025-09-22 14:17:58'),
(97, 37, 5, 'https://www.kaufland.de/product/516319092/?search_value=Kabeltasche+f%C3%BCr+Accessoires', NULL, 11.39, '2025-09-22 14:20:45'),
(98, 36, 3, 'https://de.aliexpress.com/item/1005008565651072.html?invitationCode=NWFBaHpvcW1aNE1hcWpldkowSWJIaUFSYksvYnNuT052YXh0clZSU2ZCZz0&srcSns=sns_Copy&spreadType=socialShare&social_params=61252932152&bizType=ProductDetail&spreadCode=NWFBaHpvcW1aNE1hcWpldkowSWJIaUFSYksvYnNuT052YXh0clZSU2ZCZz0&aff_fcid=fa16f61907124810a49d5c2006d2ea87-1758562297046-05002-_EwH22m2&tt=MG&aff_fsk=_EwH22m2&aff_platform=default&sk=_EwH22m2&aff_trace_key=fa16f61907124810a49d5c2006d2ea87-1758562297046-05002-_EwH22m2&shareId=612', NULL, 3.19, '2025-09-22 17:34:41');

-- --------------------------------------------------------

--
-- Table structure for table `shops`
--

CREATE TABLE `shops` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `website` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `shops`
--

INSERT INTO `shops` (`id`, `name`, `website`) VALUES
(1, 'Otto', 'https://www.otto.de'),
(2, 'Amazon', 'https://www.amazon.de'),
(3, 'AliExpress', 'https://www.aliexpress.com'),
(4, 'Temu', 'https://www.temu.de'),
(5, 'Kaufland', 'https://www.kaufland.de/');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `preis_historie`
--
ALTER TABLE `preis_historie`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_produkt_shop` (`produkt_id`,`shop_id`);

--
-- Indexes for table `produkte`
--
ALTER TABLE `produkte`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `aliexpress_product_id` (`aliexpress_product_id`);

--
-- Indexes for table `produkt_preise`
--
ALTER TABLE `produkt_preise`
  ADD PRIMARY KEY (`id`),
  ADD KEY `produkt_id` (`produkt_id`),
  ADD KEY `shop_id` (`shop_id`);

--
-- Indexes for table `shops`
--
ALTER TABLE `shops`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `preis_historie`
--
ALTER TABLE `preis_historie`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT for table `produkte`
--
ALTER TABLE `produkte`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=38;

--
-- AUTO_INCREMENT for table `produkt_preise`
--
ALTER TABLE `produkt_preise`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=99;

--
-- AUTO_INCREMENT for table `shops`
--
ALTER TABLE `shops`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `preis_historie`
--
ALTER TABLE `preis_historie`
  ADD CONSTRAINT `preis_historie_ibfk_1` FOREIGN KEY (`produkt_id`) REFERENCES `produkt_preise` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `produkt_preise`
--
ALTER TABLE `produkt_preise`
  ADD CONSTRAINT `produkt_preise_ibfk_1` FOREIGN KEY (`produkt_id`) REFERENCES `produkte` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `produkt_preise_ibfk_2` FOREIGN KEY (`shop_id`) REFERENCES `shops` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
