--
-- PostgreSQL database dump
--

\restrict aey5GQS5OREO0dJedSUEeEo2UsyEByLhkuzzYJdgaBRejtwSomlHFAUnxuKPGlK

-- Dumped from database version 18.3 (Debian 18.3-1.pgdg12+1)
-- Dumped by pg_dump version 18.3 (Debian 18.3-1.pgdg12+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: bd_erp_cayube_user
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO bd_erp_cayube_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: caixa; Type: TABLE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE TABLE public.caixa (
    id integer NOT NULL,
    tipo character varying(20),
    valor double precision,
    motivo character varying(100),
    data timestamp without time zone
);


ALTER TABLE public.caixa OWNER TO bd_erp_cayube_user;

--
-- Name: caixa_id_seq; Type: SEQUENCE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE SEQUENCE public.caixa_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.caixa_id_seq OWNER TO bd_erp_cayube_user;

--
-- Name: caixa_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bd_erp_cayube_user
--

ALTER SEQUENCE public.caixa_id_seq OWNED BY public.caixa.id;


--
-- Name: cliente; Type: TABLE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE TABLE public.cliente (
    id integer NOT NULL,
    nome character varying(100),
    local character varying(100),
    divida double precision,
    telefone character varying(20),
    senha_hash character varying(255),
    ativo boolean,
    trocar_senha_primeiro_acesso boolean
);


ALTER TABLE public.cliente OWNER TO bd_erp_cayube_user;

--
-- Name: cliente_id_seq; Type: SEQUENCE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE SEQUENCE public.cliente_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cliente_id_seq OWNER TO bd_erp_cayube_user;

--
-- Name: cliente_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bd_erp_cayube_user
--

ALTER SEQUENCE public.cliente_id_seq OWNED BY public.cliente.id;


--
-- Name: fechamento_caixa; Type: TABLE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE TABLE public.fechamento_caixa (
    id integer NOT NULL,
    data date NOT NULL,
    saldo_inicial double precision,
    entradas double precision,
    saidas double precision,
    saldo_final double precision,
    observacao character varying(200)
);


ALTER TABLE public.fechamento_caixa OWNER TO bd_erp_cayube_user;

--
-- Name: fechamento_caixa_id_seq; Type: SEQUENCE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE SEQUENCE public.fechamento_caixa_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fechamento_caixa_id_seq OWNER TO bd_erp_cayube_user;

--
-- Name: fechamento_caixa_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bd_erp_cayube_user
--

ALTER SEQUENCE public.fechamento_caixa_id_seq OWNED BY public.fechamento_caixa.id;


--
-- Name: movimentacao_estoque; Type: TABLE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE TABLE public.movimentacao_estoque (
    id integer NOT NULL,
    produto_id integer,
    tipo character varying(20),
    quantidade integer,
    motivo character varying(100),
    data timestamp without time zone
);


ALTER TABLE public.movimentacao_estoque OWNER TO bd_erp_cayube_user;

--
-- Name: movimentacao_estoque_id_seq; Type: SEQUENCE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE SEQUENCE public.movimentacao_estoque_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.movimentacao_estoque_id_seq OWNER TO bd_erp_cayube_user;

--
-- Name: movimentacao_estoque_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bd_erp_cayube_user
--

ALTER SEQUENCE public.movimentacao_estoque_id_seq OWNED BY public.movimentacao_estoque.id;


--
-- Name: movimento; Type: TABLE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE TABLE public.movimento (
    id integer NOT NULL,
    tipo character varying(20) NOT NULL,
    valor double precision NOT NULL,
    origem character varying(20) NOT NULL,
    descricao character varying(200),
    data timestamp without time zone
);


ALTER TABLE public.movimento OWNER TO bd_erp_cayube_user;

--
-- Name: movimento_estoque; Type: TABLE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE TABLE public.movimento_estoque (
    id integer NOT NULL,
    produto_id integer NOT NULL,
    tipo character varying(20) NOT NULL,
    quantidade integer NOT NULL,
    motivo character varying(100),
    data timestamp without time zone
);


ALTER TABLE public.movimento_estoque OWNER TO bd_erp_cayube_user;

--
-- Name: movimento_estoque_id_seq; Type: SEQUENCE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE SEQUENCE public.movimento_estoque_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.movimento_estoque_id_seq OWNER TO bd_erp_cayube_user;

--
-- Name: movimento_estoque_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bd_erp_cayube_user
--

ALTER SEQUENCE public.movimento_estoque_id_seq OWNED BY public.movimento_estoque.id;


--
-- Name: movimento_id_seq; Type: SEQUENCE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE SEQUENCE public.movimento_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.movimento_id_seq OWNER TO bd_erp_cayube_user;

--
-- Name: movimento_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bd_erp_cayube_user
--

ALTER SEQUENCE public.movimento_id_seq OWNED BY public.movimento.id;


--
-- Name: notificacao; Type: TABLE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE TABLE public.notificacao (
    id integer NOT NULL,
    tipo character varying(50),
    mensagem character varying(255) NOT NULL,
    lida boolean,
    data timestamp without time zone
);


ALTER TABLE public.notificacao OWNER TO bd_erp_cayube_user;

--
-- Name: notificacao_id_seq; Type: SEQUENCE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE SEQUENCE public.notificacao_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notificacao_id_seq OWNER TO bd_erp_cayube_user;

--
-- Name: notificacao_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bd_erp_cayube_user
--

ALTER SEQUENCE public.notificacao_id_seq OWNED BY public.notificacao.id;


--
-- Name: produto; Type: TABLE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE TABLE public.produto (
    id integer NOT NULL,
    nome character varying(100) NOT NULL,
    preco double precision NOT NULL,
    custo double precision,
    estoque integer
);


ALTER TABLE public.produto OWNER TO bd_erp_cayube_user;

--
-- Name: produto_id_seq; Type: SEQUENCE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE SEQUENCE public.produto_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.produto_id_seq OWNER TO bd_erp_cayube_user;

--
-- Name: produto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bd_erp_cayube_user
--

ALTER SEQUENCE public.produto_id_seq OWNED BY public.produto.id;


--
-- Name: saldo; Type: TABLE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE TABLE public.saldo (
    id integer NOT NULL,
    dinheiro double precision,
    conta double precision
);


ALTER TABLE public.saldo OWNER TO bd_erp_cayube_user;

--
-- Name: saldo_id_seq; Type: SEQUENCE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE SEQUENCE public.saldo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.saldo_id_seq OWNER TO bd_erp_cayube_user;

--
-- Name: saldo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bd_erp_cayube_user
--

ALTER SEQUENCE public.saldo_id_seq OWNED BY public.saldo.id;


--
-- Name: usuario; Type: TABLE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE TABLE public.usuario (
    id integer NOT NULL,
    nome character varying(100),
    usuario character varying(50),
    senha character varying(200),
    nivel character varying(20)
);


ALTER TABLE public.usuario OWNER TO bd_erp_cayube_user;

--
-- Name: usuario_id_seq; Type: SEQUENCE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE SEQUENCE public.usuario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuario_id_seq OWNER TO bd_erp_cayube_user;

--
-- Name: usuario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bd_erp_cayube_user
--

ALTER SEQUENCE public.usuario_id_seq OWNED BY public.usuario.id;


--
-- Name: venda; Type: TABLE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE TABLE public.venda (
    id integer NOT NULL,
    produto_id integer NOT NULL,
    cliente_id integer NOT NULL,
    quantidade integer NOT NULL,
    total double precision NOT NULL,
    pago boolean,
    forma_pagamento character varying(20),
    data timestamp without time zone,
    status_pedido character varying(30),
    status_pix character varying(30)
);


ALTER TABLE public.venda OWNER TO bd_erp_cayube_user;

--
-- Name: venda_id_seq; Type: SEQUENCE; Schema: public; Owner: bd_erp_cayube_user
--

CREATE SEQUENCE public.venda_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.venda_id_seq OWNER TO bd_erp_cayube_user;

--
-- Name: venda_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bd_erp_cayube_user
--

ALTER SEQUENCE public.venda_id_seq OWNED BY public.venda.id;


--
-- Name: caixa id; Type: DEFAULT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.caixa ALTER COLUMN id SET DEFAULT nextval('public.caixa_id_seq'::regclass);


--
-- Name: cliente id; Type: DEFAULT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.cliente ALTER COLUMN id SET DEFAULT nextval('public.cliente_id_seq'::regclass);


--
-- Name: fechamento_caixa id; Type: DEFAULT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.fechamento_caixa ALTER COLUMN id SET DEFAULT nextval('public.fechamento_caixa_id_seq'::regclass);


--
-- Name: movimentacao_estoque id; Type: DEFAULT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.movimentacao_estoque ALTER COLUMN id SET DEFAULT nextval('public.movimentacao_estoque_id_seq'::regclass);


--
-- Name: movimento id; Type: DEFAULT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.movimento ALTER COLUMN id SET DEFAULT nextval('public.movimento_id_seq'::regclass);


--
-- Name: movimento_estoque id; Type: DEFAULT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.movimento_estoque ALTER COLUMN id SET DEFAULT nextval('public.movimento_estoque_id_seq'::regclass);


--
-- Name: notificacao id; Type: DEFAULT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.notificacao ALTER COLUMN id SET DEFAULT nextval('public.notificacao_id_seq'::regclass);


--
-- Name: produto id; Type: DEFAULT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.produto ALTER COLUMN id SET DEFAULT nextval('public.produto_id_seq'::regclass);


--
-- Name: saldo id; Type: DEFAULT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.saldo ALTER COLUMN id SET DEFAULT nextval('public.saldo_id_seq'::regclass);


--
-- Name: usuario id; Type: DEFAULT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.usuario ALTER COLUMN id SET DEFAULT nextval('public.usuario_id_seq'::regclass);


--
-- Name: venda id; Type: DEFAULT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.venda ALTER COLUMN id SET DEFAULT nextval('public.venda_id_seq'::regclass);


--
-- Data for Name: caixa; Type: TABLE DATA; Schema: public; Owner: bd_erp_cayube_user
--

COPY public.caixa (id, tipo, valor, motivo, data) FROM stdin;
\.


--
-- Data for Name: cliente; Type: TABLE DATA; Schema: public; Owner: bd_erp_cayube_user
--

COPY public.cliente (id, nome, local, divida, telefone, senha_hash, ativo, trocar_senha_primeiro_acesso) FROM stdin;
2	Joseildo Nascimento	Escola Fernando Soares	0	11932407441	scrypt:32768:8:1$PUoeMuCzpLxdwCEk$5034e17c72b413bc59f7602e4d40adad402a5a27172604922f30849ef0813669417a478b33d4a2350562b1caad862188f0a7c9850609c8692cd92cc92822e9ae	t	f
15	Edvaldo Rodrigues Galvão	Flexis	14	11973850785	scrypt:32768:8:1$M6XsYBURMdC1JlNX$6777f0a1dfd21b2a046faca5a8a028b308705ed648f79da5292af628924220ba858c18aa6add8d956ecca41e35b7f3302f9808ba92ba41da0c1966c86bd54e3d	t	t
10	Ana Lucia Soares	Casa	0	11957167957	scrypt:32768:8:1$SBQxUsFdj7WSFiZu$fcebcfe1814be5d82defe5d4ba799c695651774e38b40029fd66a673111f7b2f350109c94292e50ea10763232eda8faa237b3cc0e49371b49221fa2259911aa6	t	t
13	Bruna Rafaela Soares Silva	Casa	0	11932420407	scrypt:32768:8:1$qf52SCSWyPfK4wqO$ae53d1c8bcfde75fef7cae1aca4357dc1518fa3d4172db51262af0a0f6661255f40a1c4dc387e155d225c38213a7ae5b736aa40f8f8a50df221e05d5f37f858e	t	t
14	Eder Henrique Gomes	Flexis	0	11910295853	scrypt:32768:8:1$xpIZ9EEJBZfjkdi0$00a40dc92ebe1f88da516648c000c5ebc64879fcc815533b43ab6d698829bf119719c74ce676420a28db73328a4242031f4b142ee625b633b3edd1895a5b9a1e	t	t
16	Hector Nathan Virgilio	Revistaria Allil	0	11998783292	scrypt:32768:8:1$pEQIN13DP1GEJ772$0fccbcea30b46e6c084ca24d35e85d097d6f6b7c4c4c5219ae582f77b32dd6c52867074ad2acfe4c7d161625d68ffb91d609a69745c1533237c0c529a0935c1a	t	t
28	Marcelo Alves Pereira	Flexis	24	11994517695	scrypt:32768:8:1$ndtE6tw6PgJM4nLt$36564fff929f3fabc5cf1d4d27bb611df0ed60f8b49f574ed6a8a71bd20aa063b51a433e61c3a39788dde3b3fe8ae7a74b3e8cb2267b4d9d510b2e6efaa29f38	t	t
23	Rafael Latorre Teles	Flexis	35	11951341204	scrypt:32768:8:1$BWctcDJvCf7dIFUv$bc9db1e2e1f67ae7145a577cedb740d295f8760fd8445d7bd9f3d6ed7cd74698e60cd51c15b8aeebf24773f3e5c059b2c7251696fe3997f25d933aa86a2ef2a1	t	f
19	Luzia Cardoso da Silva	Casa	19	11996702139	scrypt:32768:8:1$4EtkIIHAijcxVjKA$ecdef79579568511423728b8885b0c9b7aee9e3d7b4954e749742739bd9ee195a74231d08d3c68f41089d78e94859846badc05e2940104501e53abde9179b2cb	t	f
25	Andrei Victor Pereira	CASA	8	11947380357	scrypt:32768:8:1$CUBiK6JHvB5gw1Cj$8399de45d13ce69665428fe3012b499e9c5fa09ce69335bd69302870839694adf527a00da21c4b9d515b9a96ed945bc862356d4e6f4918751fa8d3ed3a746627	t	t
4	Wellington Cunha Gregorio	Flexis	44	11995702464	scrypt:32768:8:1$dfjBeRYN5jgcABTQ$6730ff00b5e495c33dee0486c1b7c5517a0c64f8ee69c80137e0617f7bc04f4a15c371f2c5ced075a4aaa6f326dcf911eb3dbdc6aedbea6a7f807f9a86663f74	t	t
5	Josivan do Nascimento Batista	Flexis	48	11998022945	scrypt:32768:8:1$fMzqQbiPZSTh8IR2$fdea2083adf25f5f02b21f6e8c0e72a0c891fb9bd1d61d11598cc994f5d1ba0dd86c6ed01601c8d4fb46aeb8e99feedc16e5bbc44f15330d54d8157b2f590138	t	f
26	Mario Tadeu Alves Pereira	Flexis	13	11950866009	scrypt:32768:8:1$UeONyvUL7c6G0PpZ$73f71ac165cf8760e8abd2fdfc0cf92516f4b0a9cd2142c40a7b4b795fb5911ac6c6a7bb46c2c096139931de6553ce512f8fd62bf20031cd160100b0fad13d32	t	t
9	Renato da Silva Pereira	Flexis	20	11934164435	scrypt:32768:8:1$fFiurEjOLx0FSMEE$3e4ff434a5bdae2688408abbb429bf4798f3c99fe1d8c3320c7d603427907b4e08b05c2bdae24288ec89c34473b848e15c56ace494b0dffc8391fbff915f5710	t	t
30	Roni Araujo dos Santos	Flexis	46	11934666733	scrypt:32768:8:1$UTyB2t3Oi61rroyR$61fff80d3b7dbfe5c0f8bd5d634e1c18c55bd3799c28d8842fb900cce989f096e94a98dae54d88160899fec88a18ab6fe74bf8ea167c2cd4c2b5ad0083eb541b	t	t
6	Tiago Etelvino Freitas	Flexis	0	11947077150	scrypt:32768:8:1$0R7LnOILjATZfD3f$8bee7ffdab35de3473f2b8fec1cebe580f74578222b246507d38e29a39b370a14bb7c5bfdce2a39cf4c47fb630ac70a347dc98b21668e25241526b850e247b3f	t	t
1	Bruno Henrique Cardoso Silva	Casa	0	11999939444	scrypt:32768:8:1$nmTQs4Gjmz6kRGHF$ef7ecce1abe5ca47d6276b4e194a3b64cc7d28f7286967b1b31abdff0c2340d56cd7800073e6f4e9318a0821e10a092d95ad7b0b0eb4e492b31ab79d24b8c640	t	f
17	Jaqueline Ferreira Durteia	Revistaria Allil	8	11946045431	scrypt:32768:8:1$wu9zJOwkGLqu0RH3$cad638f4a81798caaae207023f45fed22d72283f8828411df64935446bdc3fbf8fae9d8f2f5299184caa2257c4e56bfbbb855991388d3cf60dbb643938ceb1b2	t	t
29	João Maria de Almeida	Flexis	30	11988339463	scrypt:32768:8:1$aDAHwvCewvTggcFD$13d4c1e33d08d8cfc2ca971932da79fadec43bc13df060e9352ff9ad007ca151fa7761b8546495fd29ddb5405785ba0a1217c6087ea107d72e683ecc2e9b41e6	t	t
7	Elton Luis Simões	Flexis	12	11991488199	scrypt:32768:8:1$JFzHr7TWcXl107RD$8cd20ce6ebd4ca035b02a0d8e665fe74b6407dec855aa0b723255f4c7fd8ba3e65a7b17ba15d031b0a8934759c7c31be9822becb8b14846bc1d4b0d31bf83a8d	t	t
27	Ryan Alves de Souza	Flexis	38	11932248923	scrypt:32768:8:1$wgmQcxKR355VQ8l4$ccb3c77c8f7701617aea62f078401c7c953a8937fb0a668b345a1919723d692ed20ed7182655867a6a7a78ef560493495323da57211f21fbd806a19cd4689d49	t	t
8	Luiz Antônio dos Santos Carcelen	Flexis	0	11970947216	scrypt:32768:8:1$O9UNbkRUMZIQLpYS$93ebc76e4ea799489ef0d1cbd07161146d03e839d169dc47d298a16cf470c92b39b30c142ce5fecfd346d227b1dbe0b04d85b8e86d6ad554a26542b562b87878	t	t
22	Orestes dos Santos Reis	Flexis	7	11971465096	scrypt:32768:8:1$zXb0NQ7jt9vHt3yr$479defb8651e75d61b29d7accfc0edc7f9de137dd0e7668fd25590f5de5932c1a024c532d5f5d49c0db761a9d94917621c5be6347ee12cd1a6c32578b2c45f5b	t	t
3	Maria Paiva	Escola Fernando Soares	7	11975973494	scrypt:32768:8:1$zjopdaBwESLB52ty$43f928d3c6d38013023918013389463d3d9092578479165927bcce31ab38b799ca84098b96b913ad173f4d1e34ce10e15173d2c032caca0d7ad9090105d46056	t	t
20	Maria Clara Clorado Gomes	Flexis	0	11965419731	scrypt:32768:8:1$u9IsnFoJ6LgLMyf0$5cc09da1093f1c816ecba0dc31ee4c1e520d982784b14db027edd42eccb76f500e100b3a507460cff4f8604fb25364176e26b36f4ce17185f16016892cf13587	t	t
24	Rafael Reis	Flexis	84	11919083801	scrypt:32768:8:1$ppOS23lovGmfGd6p$83b56be3e940e3cfebf9dae868ce25266d055457b56c2266f343301270aa720bc83655c8935c5fae435aa7b37c6dd7ecb002bd06a63ca02df4d9bc71d6a3c8fd	t	t
21	Mirela da Silva	Salgadaria	0	11934461604	scrypt:32768:8:1$GiKArXDgYz3sIqwt$866c75806a6b0e028cedb0ff123ac156b4cb1504c2bdd98d83a70797a8fef8a839bda6e32ae8ffe0a32c29f7345e5023c14328978391e187fafbe1d245ee457e	t	f
18	Jhordan Rodrigues de Sales	Flexis	96	11932171172	scrypt:32768:8:1$g0fnEBrH5DvmDvE5$86d01c2418cfbca8afdcd6a895f5e0779af426022614734b7852891df5cf6e122bd79925cb817a9828a3bf3d3b9cc98773490ffbdf7f81377508616e414ea16e	t	f
12	Antonio Aparecido de Melo	Flexis	15	11954949114	scrypt:32768:8:1$E7rr0s0tHphaldDO$c1cd986aeb4e8bb14a86c3a892e4177c61edf69dd19ecd71cf86a62387d3047deb599ca0951a0dd01089ea02eaa6dd2a85c276764ce79206a22a554d7a4698e2	t	f
11	Antônio Angelo de Souza	Chaveiro Ponto Smart	40	11974774915	scrypt:32768:8:1$lRsSX1YsJqWvkl3E$5e7f375b3a876850bec79d61f5d9652a264567ae33173e8941945f9a5b9e7541959c5272834a8191253a7a00daf86f86d9ed9ca7f58763c87f5ed17ac81bde04	t	f
35	Eder Gomes	Flexis	0	11994247497	scrypt:32768:8:1$A0VwNScO7pHiRqE7$6e5acb828e0fb18f84cdf5e82a33d3b6a45457da07e7216ee3914bc3915090ce52b6766fabc1906c80713ade8cb10b7cfc6ef2ec790fd14d19cd1e67b531f18c	t	t
32	Carlos Gustavo da Silva	Flexis	7	11913222621	scrypt:32768:8:1$wV8uQ2GFjBDShobt$edfa230fe9ad0a4249f7c5c6ecd0ebe82f3fe8b1a353c7f4a5c9417a42d9b113a9097dc081665d964bd0a7f28713a13a6febb43e36b7fdc50f3b51c1507c5810	t	t
52	Miriam Reparo	Ability	0	11950577605	scrypt:32768:8:1$wfQCdBzUycSFXdfJ$9e798a11af60ec701708de8566093279269b52cfb3547b0d25efcd4aa8441246ef6a6625d77896809035d13683c54047630e5f45a5a3deff3f4ab3d6a9778da7	t	t
31	Samuel de Souza Fraga	Escola Fernando Soares	35	11972307733	scrypt:32768:8:1$za83TQkcBtkgZkQh$6047161e1d12dea5b3053daec46086c2b5cfdeb7e2e41a5003fc930cedbba373583494aac2c34ff146ff0fe09808553fc19b1b6c4420e6c4e742aee634e74a65	t	f
36	Tiago Henrique Gomes	Flexis	16	11962565295	scrypt:32768:8:1$STyrMFqcnzkH1cL2$62dd2d8837cba3e6b2f71cc5e049ee548a5b74efe9955b668babba7a9815a1d5279224f28fc4508686132e276c6884c3f63e86c2e2a579c4b4085fe5e8a9e832	t	t
37	Renato Lourenço	Flexis	21	11934318994	scrypt:32768:8:1$8V9lh9c7ak22VZV9$faa8af60e4cefc48b828255f2e194a8050497004def1ed85472393dbfa8ebedfa957b47c5a0c87762fffd0c8cadf17c1ebbc46be276b65f59939ba30f342265d	t	t
38	Hebert BigPlast	Big Plast	7	11973361382	scrypt:32768:8:1$FT1RxoC1Nrlue6DD$452e9b1ff16f56635d3b7ff3ba2fb69e059d552f745b058613165aafdc10e427a83f3386f03eb0718a60c215d7785e669200eaa37263f504e763ee57bcda8e34	t	t
39	Laudiceia Coral	Igreja São Judas	0	11980757454	scrypt:32768:8:1$INu000O8BBn0fD46$dd305de2b3fcd85242962cdd082c4eee5f9243dc9daebe1ebfd82d6591bb39ffaea748c90cdaa9b6a37b9888f0c0ba26aa62bce188bd22fba29a1dd05ca849c3	t	t
40	Dona Joana Gomes	Igreja São Judas	7	11957026061	scrypt:32768:8:1$qt6HMbVS6S3XSUZs$7c4d8eaad78284f93c345d1366e63228461a6f3b88ed71b44ca7af6c7a73d1a576aa161ebb7d892eadfb987c64673fcacdf6221ca031f8b065055467e28e63f8	t	t
41	Eliana Coral	Igreja São Judas	6	11997019987	scrypt:32768:8:1$734ifAmSAcHHrPar$3dc533b0f7228a2ceb0cc7631391c0f8763efe97fc025905b41d74770e41485dc715f20fbc17c2811604631950e098e3d1ae0d4525c7c53560eff9b6c7ff4fc9	t	t
42	Bernadete Igreja	Igreja São Judas	16	\N	scrypt:32768:8:1$rLcxoIGCRGqOY9vA$9b4c532c0c43fe52135c6c54bf69d442c12906be9fafdb488b7b2fbd30a8a9994d1dea2ec023e5c408e7bc2fd5996a4f3b29fe67e2ef4164f105d29955d46cad	t	t
43	Mayara Ability	Ability	33	\N	scrypt:32768:8:1$8EQz24bOuDnJGSHW$dc8ae1ab9111c39354d7c33c8764368a29f652d8fb5e57adb8739069e8fe4b05ce7adaac071640c22038f69ff1652745ef470d682c28028f40fb0877b3c5199d	t	t
53	Victor Fibra	Ability	0	\N	scrypt:32768:8:1$0lT4F6Mn95dx3lUA$c66f99f4eae775e7c714cd26844adb1cf9b89b4cdeae8a01e7a31ad09d9613774fc4459c79bae721cc5d76250a373aab514ba6a7ecb4c036860bb262b54c1ecf	t	t
51	Bruno	Raydeec	0	11995005293	scrypt:32768:8:1$oEiPxsrRwLNvTaY4$bbaa3ae3329cc5b1d770b2ce17a1ade36967672895a6d9f7bece85e2a1635974b3c48c8639ec84a37a6a29ac575f9ca4b3a881e5a207c4c7ab40fba5b6e00493	t	t
50	Cabeleireiro Ediel	Raydeec	0	11998592498	scrypt:32768:8:1$27E4J1gKVdrNQgak$bb31459566836e25ec17dbba22156c36998cc1a8e956442262a84e18fdd237e24dc1e596a5ab7f82246f8cf8dacc62c99827313328f21d3668e04b6872fe19f9	t	t
33	Wilson	Casa Lua	24	11972879783	scrypt:32768:8:1$lvmrBC40ubcZxQOq$b6075ace3bdb207da1a74ae7eec1fd3641b48396e68d72515d4f80627b4bbba609e5dacdeb409133fc56d09bc7ee0d5c23d47b27a027126b33f32f245805f967	t	f
56	João Victor Reparo	Ability	35	11947963457	scrypt:32768:8:1$XN9WS3KF0KcNLb2z$3520f03f3b4f2965935a5559c4b4bd348aa138be2ebf3542b0100508003f61741499d93f729764c70eb3bcf9045637136eeea059a6448d3b928c48f081ddb6f2	t	t
44	Elaine Vivo	Ability	7	\N	scrypt:32768:8:1$w4C2EFVWwksqPIFs$91f2c7a2dae2e80ee920dc08c527b5523caec690794f06b914ec0161935dc44442a24df38ac15be7dae601be627937e11b83fecb513d9fcfc6ed1ea93fb0ea4b	t	t
47	Professora Caroline	Escola Fernando Soares	0	11976081980	scrypt:32768:8:1$HHG3Laz5FKTmVZgV$27abe4ce0c1232325926cc3e3a18d4cfd3dbe26abcc7f4c1f383ee45f2fd533f67972819fe580c0a3683d108b2a2a869fb78e88af0a53d6772011651d00be2e8	t	t
48	Professora Gislaine	Escola Fernando Soares	8	11998616133	scrypt:32768:8:1$UckGedkq7LFERwuW$b628d94b857253a1d4f094094ce966a32f163c02707e0eed08f1dc83723d016700c65c64ffd7b7c24cc5d79972c13a188b84b0c28b66675becd8b9367df3f578	t	t
49	Cabeleireiro Rai	Raydeec	0	11985354581	scrypt:32768:8:1$pjIBcdd4SqHGgybU$ba07e24e3781553e541f9443f6aed659abbb81761f020961a946522a91132d74ff45d3d67f8cb6643fce8d1055f98de65e710947026b28bf9768b0433af34f74	t	t
34	Ademir da Silva Ramos	Flexis	0	11998959904	scrypt:32768:8:1$ipOFsLCnT2S3VzQf$56a81391b458b5cefeda457f78bfca39fd38c3d2570500a6442a9caa3d5ac18e21a844160b4cf053a2907c3b422696c511c92552756d107f8e644523cf50403f	t	t
54	Tatiane Planejamento	Ability	0	11987746814	scrypt:32768:8:1$GsdvJ7SjNQDdwXWY$0254f9943f0f5d51a1956a4218af1d0b741f78f8166d0655ea55379dea1f405cb994a8faa8f2c944191e6e1d9a8f852f52430c965850a600abc705fb81540afd	t	t
55	Luiz Planejamento	Ability	0		scrypt:32768:8:1$SbUkaHToKgsmYwVB$4d6dff18801f99733489b030e3b147e4dde260189a86ac60ddf8a4873f7ba3ddf3faa42a54b28edbc4ca8e47f9285851370691fb2a1c4b611d6ecd2b1357ba56	t	t
58	Paulo Fibra	Ability	14	\N	scrypt:32768:8:1$Xti6fRZQygOGSkUK$a4fc4268a008c25bb0cd93e0a24ed882139ae078295bb88f1ea05d1d9a1363568c1321d0decfc091212eaa3f5d9da6632f1df7f58085cb790bd34f1b96965439	t	t
59	Ianca Coordenadora	Ability	8	12996657713	scrypt:32768:8:1$Vrlq1cN0uZlMcLrR$ec3595b62626ccd91bc0baf02cdef4b3792ef4311c5f2b1f2f9c12caa83ae53780339cec1e6166192a323fcb14ab4edb97089eb4cd34e3828620c48e92443760	t	t
46	Vaguiner Fermino dos Santos	Flexis	0	11971568663	scrypt:32768:8:1$ZHWghBq1hwWxuEPl$212c851a87afe1e8db0223cf6df4b40ca8793498a1e15376b0bd9165894cf87d8f441ccf78b4bd2118e1f34e295babcc49358e1d1eb838d4efa2dea92e1e3598	t	t
61	Lucas Fibra	ability	8	11965255250	scrypt:32768:8:1$Hk8RwhkAUtt8SQcj$c496a8ed04c7205013f2f6bbe66618bb7a8bc55850d56422680cd3a6d4735e07d5f24effee41a08abe7fbc38b3bbdfa719915efde5f4c67089f4a20af528acc1	t	t
45	Maria Lucia Soares	Casa	78	11930563828	scrypt:32768:8:1$Iw1GvIBvZXY6mk8L$577d3d7f23a25b0eff3ef9dcdfab7702ecfefb7de1a64cf9b9fd0da5b6085a131c1c23308ac885e16217f2ab08ff30cbd3d01e9011e8245a1603b58f0b0cdc39	t	t
60	Sandy Home Conect	Ability	16	11981322836	scrypt:32768:8:1$xwNsV4vvsex7Svi2$5881ee152cb76f147565ed45d406621e9d7fd4eb2f6b2244e0355e2612a3f760a8d2485c4fc6f50b11dd14e791ea93554cd174c6223bf63242faf2bde4d82ab3	t	t
63	Loroza Supervisor	Ability	8	11910111214	scrypt:32768:8:1$JD027neYY5h7kGJO$0ce29acf285a1495d4c13f86a8f57cbc62bb256f1a03179fb4b5051b959fa2ef4590f3725649e50ec4041cadc753028bc9582c7c7c2635c349588a5a04832a07	t	t
64	Gabizynha Implantação	Ability	16	88888888888	scrypt:32768:8:1$j83sAML3g2tijg0K$dcc1f515574f8fa51978e867b701b39df01c5b6d1bf7b02dfe601f7afe62b7660a0f7a606cf91c5f1fe53cd389a106f705be5d639a1b075596821dde5a320904	t	t
65	Luiz Implantação	Ability	6	11789566466	scrypt:32768:8:1$xmovqFoAeaf1ybMZ$273569862ae50328dd9bdbae263faaa506d4e94b2a9a2d886eb343e8bf9f77d6bdf129767a048fa6fea407ebe760fcbed5f007f5aa528438f05a5d4cf358109a	t	t
67	Cecila Limpeza	Ability	12	11988922806	scrypt:32768:8:1$L4MFQgUFz2VDGXSQ$62039330ae9dab074ae486a08a57b4ef111c5d4849ed3d931a13a529703ea89f5d9545f83b8a0bb1de72766b924e5a5e84d486b62bd0486733ad23c4af0662e2	t	t
66	Renato	Ability	0	11960614415	scrypt:32768:8:1$unBvjCsUm2kEhjwg$34a7a82d7d2dc37ae313bc44a3a195ef4c5f54b50099a40c89a09ac2e7158262e94954942ae03d579a79e72db9fd2dcadf93f4e65ef43e0a8840577ecddae80c	t	t
79	JULIA COMPRAS	Ability	0	22222222222	scrypt:32768:8:1$rgA7a22dyoxQ15IE$9ff80364f34903879c41d46d6379480dab626b8d58d8032536240e491033ae7fb6e5689afbef579584073b54ff96d4ab20e90490f9698318466fdcecf43b34af	t	t
70	Monica Vital	Ability	8	11997920557	scrypt:32768:8:1$HOG0N5QRFXa87ywc$c512cbdd61ff4d95f9b7220e43f43c563b15b724679ee0c569e1f8fcd20115d5a7e45aab49c315741a5294646ad95e71774aa6531e9603bf9c154f0979f73102	t	t
71	Jessica Planejamento	Ability	8	\N	scrypt:32768:8:1$4B18qdP4JAS08F72$a879e24f63d6a01da4b47f12b2da582f2fb45c2e699b8c96f6cdc9989222fc447590df99a0508ebce57dbbe37fc7d1348784dd4a6e184a1b22cf269ed9d0f6c1	t	t
73	Amir Alves Pereiraq	Flexis	0	11987708172	scrypt:32768:8:1$Ma571l2kDGA7UA2E$92ab452a6f1d132df6bdc27278d71a04587ddd1f7e3e6d483a9e5b849c352bbc5d2070429e7646acc46d0a0b2fc0b56817aa22199818fa67b29a722be68328b3	t	t
72	Marcos Santos da Silva	Empório Mineiro	45	11930574942	scrypt:32768:8:1$doGx20y5mooaBPFU$3c11dc656e51b4e60089a027536c334fa14977f9ae7bcfb370c005f683ce72456148eb337b8432569cf00c65fde6cc46596839276463a67087968bcdac96c7d8	t	t
76	Luiz Simon	Fisio	0	11975202789	scrypt:32768:8:1$fEuv01ukEYgATAx9$3a791d04e930972d8d415c190439e56e593fdb9b3731334f894da06bef8341696f3a2587acbdcae9bcc304e4fe7b8c94a06045672f6a1d0216b92a6d6dbf3c47	t	t
62	Renato Fibra	Ability	8	\N	scrypt:32768:8:1$R3F1CtprLeqXG3Br$fe95b210283e00763c3fa2e536df72a21b5d19b7821a7ce4f964a3eb8492aed339e391c286a880fa49f7b528ace10c0285b0a5ae6930271436e821ce6a783150	t	t
89	Alexandre	Escola Armando Sestini	0	11917246712	scrypt:32768:8:1$SwkH7ELlUGsva3bH$468890e74654080717e24672fade84974182f8f839fabc5e29e790f5978d3119b259371aab7f329bd1deba753cad5e57228b36b9ef5648e5744d875a700f45dc	t	t
74	Flavia Vizinha Ana	Casa	43	\N	scrypt:32768:8:1$ob8v7Soasv2qXvfF$05f0165fa53440d3c4ad4b7f86213a0f457c7239606f487ec9cc3a8b76d516f83e8757d803ed51445ea365b70c4552ac47d4afe1fcd41811ce765f7516f0c53e	t	t
85	Emanuele	Escola Armando Sestini	0	11971803630	scrypt:32768:8:1$9GoUY1RNzctoU56V$cf629910148d2c7836890861caabcd0175ba9234f41574dd35e49242f9debaa3bc5e8fcab4ebb088ead7544a06703f722769f37784c9b6890a675147f5c4e04a	t	t
75	Evandro Alves Pereira	Flexis	8	11946077083	scrypt:32768:8:1$FzJ7fj6g0DmDSWWF$5d8dc8815cf63548b1465051b3637335dd429f80e60ff5b4a22ef6533794f169bbb139bbfc0cfc1f4bd25bc2f064f3601b6d32de155283cb74383127ffce7b6f	t	t
68	Agda Vivo	Ability	0	11951258718	scrypt:32768:8:1$rYG1xf5oQ6L4HXAc$fe7faef69d631a28cd17e0fe1367a0fca4c61db04323e573323b58b56210189c69ed1e09ea3f8b236e42feac4e551bebe3b0bc7abd4e2d6cdf6fcbdb68817f22	t	t
78	SHIRLEY HOME CONECT	Ability	21	11111111111	scrypt:32768:8:1$fidUIQOkOkHnx3VT$60d7db988a10b5a0a2b5f6599300128e8797b5d132989d72eabc26c36b86be82e4b4ce51181228692910985e1e7dc2c813ce022fac918dd885763849975f6f5f	t	t
80	FERNANDO COMPRAS	Ability	7	33333333333	scrypt:32768:8:1$vrCF4ABlhLYF3YwF$d02a29b91bb12cba84be396eeb233b9eeebbfeb62d4385510e80ab5117b0cd6b415206113d9721bce01cf20f57d1a61b0c924fe174cdfad1bb81948516b5fd50	t	t
81	CAMELO SUPERVISOR	Ability	9	44444444444	scrypt:32768:8:1$mWcwSqPrCcC2L2Nk$545491c2a32e3d82ac4f58360b364b5fcd6f04c7729cc40c57bc53a33372288496758a877b0b79dd701cda2626a30871f9063f0179da85b414ebeae1a03da1dd	t	t
84	Julia Limão	Escola Armando Sestini	8	11992246120	scrypt:32768:8:1$1X0NIa9dJNeNbKzo$081de4c71fdec340f7619a3d221e944810b509f542ead8a8312316842e2ec596715488665806f67ff5090a80af956f6241f6034076f9ccb8b329340b3720deec	t	t
82	Marina	Escola Armando Sestini	15	11966811580	scrypt:32768:8:1$zgvfKy3vCvjcGXqt$4302ca9b94b909b77551bb69f89ec893c50b48b5278d4b9d7d645fe3e1665582298cb552405b7bb24f8ec5e81e94ec7952fc184a7da0f11b86265c01a3233e5a	t	t
83	Maria Eduarda	Escola Armando Sestini	15	11916718197	scrypt:32768:8:1$eZ3gSqO3deG274nv$6672fd08fe034a0d90470f2ab92b031ca588b1bb591c1b1bf0e53ef4c3453c33bfee7776c7cfb4d7bb9d66dc572053e99e71618c3d12db93ab70bfff7dde28ce	t	t
86	Lana	Escola Armando Sestini	8	11955588165	scrypt:32768:8:1$aolj1cq13hDLjhWd$9c4d21bd4f45de9a433cb68abf90f8b75fd9a664395024cce2470b38ee81cbc7e7119d92e54e240cf46557920391c5cb8e4982adefd16c79c59ebb30c23609f1	t	t
87	Tauany	Escola Armando Sestini	8	11934846071	scrypt:32768:8:1$5mk8TEFGBr8lK4t2$e26193ca439e8be99809064576410cc9db28d1fcfe6efb58f48857687cae031543f0618f0d3cc70f4616dea8f9320d398e9aed34bf9a4a598f1e2d4ca79ead92	t	t
88	Karol	Escola Armando Sestini	12	11915940519	scrypt:32768:8:1$eVb4CbYyzdHtDahx$d7ef6ee642d41e8b9c386ffe7b97ca401a1ffa59de4247458cf262f82239d62fb4fa8cb83ab66e145eac761bfac5602fe8977b47718125bbe78a25b52ae61bcd	t	t
90	Adma Limpeza	Escola Fernando Soares	13	\N	scrypt:32768:8:1$IEw75pcJjq9ujl3n$05899cf8ddc71c7df4c85fc1fef4bf2f5a88b624a134cbae16b62b6dda6e28af2e7a3191632c0ec13d903ef7ec9e92b90beb018cc6a396c2eb1892ef33e438da	t	t
91	Kelly Cristina	Farmacia Beto	0	\N	scrypt:32768:8:1$D5UkUv6ajKGXNP58$49ae1bd90ffb166894100feec6bdefc5f02b21700b2512ee9ed170008b02cff88fdd9ecbe14ef2b58126e64ef234d70801f3894f6c2a53956f3baa58162d04f5	t	t
92	Alessandra	Farmacia Beto	0	\N	scrypt:32768:8:1$F369DhOGzbArDcqw$01e0544a878d1c295e25a081841a59e77cdbac38d0baea15db1e4a3a1305f793656d471d7a03f8fb557132ce3cb12c93dc9fa47c40a51fd8b5e534fb496ee579	t	t
93	Marcia	Farmacia Beto	0	\N	scrypt:32768:8:1$UzAMp3BQkNekWhUr$9957021cedcd415892bc33d6e2e4c6aa254d34d915f7e8b6f0d0ab4123c7f0ad14dc5e83b7ccf0eed3e7e52012470cde62d4492b115c83ad904061fa8ba597de	t	t
94	Marcelo	Farmacia Beto	0	\N	scrypt:32768:8:1$1fFp0gm5wNF3v2ih$b1cd7839ad28bfefa742b9f8eecb2d76dc36d67d935bdb779533f390f08d0ccbfe949bc98bef6575be993e0f7b01231df9b14d2edb8bb2afedfd540ae552260f	t	t
95	Beto	Farmacia Beto	0	\N	scrypt:32768:8:1$wOTEhnhJJ8VBl3hr$6193ddd2f1d7a2eb122ece622fa51dc0054f9963d2a8bace524aaccb6096f479753f91bb722a8240c2ee9a968413673ab4fd770a5432b09c2447b1a5eacc2147	t	t
69	Ivan Supervisor	Ability	0	11946073110	scrypt:32768:8:1$PXNEkZNLGRifz4Py$70c14229884b477b6ba919cab6484e3fc73177a0d04a4f9561eee598088c941923c8b332566679ac08d2aa4f43673e0dd4960591a7e71b6acd824e58836e604d	t	t
98	Cris Vivo	Ability	0	\N	scrypt:32768:8:1$ArK0F8MrfI3p8KLy$bdb873f14db3d57038cf4510cc8b340068d1287cfebdcd908af3fb604cae2cad531665571608cde75a2911b0a4626a271b3c5ebe924ea8fe5ef7a51ffd19764e	t	t
96	Maria Limpeza	Ability	6	\N	scrypt:32768:8:1$R73s6LHIti3TapjJ$175399ea6ec4bdafc1a7277413d569ffe77de6e2230aeb48c58584e0e97ead646af6cfd6eb6f6592ea7c3f532b9e2e0b5dc2f39f36f6f1f0300f9cdaad4123ba	t	t
97	Zuleide Limpeza	Ability	6	\N	scrypt:32768:8:1$Hlkz5qm0U3pZRGHS$3d0f93e58bc71d1105ad14a7aef4550d29b852cc9b2932aa48c67103833febea97bf69e6cc226118e06fb4cebb3a76edb39186cac4b80a76b3d39e57d578065e	t	t
100	Janderson	Ability	8	\N	scrypt:32768:8:1$HotV5jQa0MznVKwd$d17fa91669e8d21590898f4e3a50841b28d17bf7bd7ce69ea37a42c2ef61662b5312baa2f15d9d3214eca879235f0c741841b106c21e8412637e9e0a68a65bc4	t	t
99	Monalisa	Ability	24	\N	scrypt:32768:8:1$txPnfVTAy3JEJkMG$3c5b4697ff4e9c70c92039cf4a5d3a00fad3948dd09d5ef753305806fb783661e3baa652c36da866b1857d54754ebadb57b4d20c4852e84e126aa5f90d06a18c	t	t
103	Tatiane	Igreja São judas	0	\N	scrypt:32768:8:1$TEMyAds0Af9tSE3c$adb1cafa6d3db7afc4ee1ff0e4f622ba43c8a3778f0acd15b9a69a31fcf054c5ff462140846d552df8fa64f768bda5b18c94da20476b89756965fb80fe904f91	t	t
102	Ana Priscila coral	Igreja São judas	21	\N	scrypt:32768:8:1$zfp9w4ahzW2Cvhaw$4159fd8078300092e1c8de9883d4ce172a96ca0dd78342a5aab5633007cd4670859baa5aa25d6ea7240fc40c7ce6c73ca8d1f460d08185629941ec5d3304e264	t	t
110	Janayne vivo	Ability	7	11970222022	scrypt:32768:8:1$k3L4TL52oq18suwV$636849b6bf99daea2246d002086b044516c4b2a1b31c390f1b11d82e173d1a90447b7d66fed81b582ddac595935e3a8973826de90d02a08b8f34cc8e8ef7a1ed	t	t
106	Veio	MC veio	0	\N	scrypt:32768:8:1$C7nbafDaLb20r5YU$4384f495b935a173ffb73b6fcc3adf427e050e1740a5e747c473672758cd1889ccc8ee624a5374404a2fd60a03d4956f02c544a918dae91bf01aa6ba06b7ac67	t	t
104	Zenilda	Igreja São judas	0	\N	scrypt:32768:8:1$ksH9doHF5NaslSu2$243feef16e069c4627b9702e594d507360e98b7a80f80091e8476b63fc64780d3d06cc6e2cc3c7e85fdeafaee48e2643fe0668a063d326b76ad07ef771610a45	t	t
105	Genilda	Igreja São judas	0	\N	scrypt:32768:8:1$pTuuckISsofDzNtv$472a0fb64d8976279515d4adfc13b16a68895ef92a39d5326baaf9bdc963e5ca20a2668799a317606d043a5c44ec93ecdb4a82245a587f8f0c72508d9380b7ba	t	t
107	Thainá Home Conect	Ability	6	\N	scrypt:32768:8:1$Qq0ykzkwMyg0iWVZ$5a67ce4a0d7aed8f6d16e766dff2487fb049b8df720b94920d7e2b9c1901fe7705218616853209ccce91f02a47a8bbd5832c69e3abb602ae680ec2fc541f5834	t	t
101	Cleiton Supervisor	Ability	52	\N	scrypt:32768:8:1$tIjbpGx0pExSYf64$bd6d5a748795df6b40efff82877aa89a3022a212a7f303b11b3c13a009081f729a3a48294ae4cc795a25ae8ec4138f719c7f080a061db43bf709254018fe92d5	t	t
111	Beatriz Reparo	Ability	7	\N	scrypt:32768:8:1$QdcM9QNVzmECoGj6$e060bf4ffc7386f970435391a67e1b98a2f741c0349899b0885a1143d3998a6ce9e3bd5434692fd362ee7df35a942ad2314ac855fee713bc3c688d92b205eee4	t	t
108	Marcinha vivo	Ability	0	11992745695	scrypt:32768:8:1$D3BcQ0dsV522bho1$b361b61a5806454c96510eaba82f7d59e2634ebe4aa27616dabfd00141cbf4623a3a69849f781bc6fe31e4c9ecc30beb260c5e137ed693c328eff6e5004ba201	t	t
109	Jessica vivo	Ability	7	11973275420	scrypt:32768:8:1$XoY1XccPvxFwwR64$a3390857830eed6345b244830c411a9b4ce39e5b7e51a537c64ab460a38469472bae2ebac0120a8d54e26d3e0366b6b43263af83382b347a1b78e5bedd07b6fa	t	t
\.


--
-- Data for Name: fechamento_caixa; Type: TABLE DATA; Schema: public; Owner: bd_erp_cayube_user
--

COPY public.fechamento_caixa (id, data, saldo_inicial, entradas, saidas, saldo_final, observacao) FROM stdin;
1	2026-04-10	0	0	0	743.79	09/04/2026
2	2026-04-14	0	0	0	284.31999999999994	Fechamento14/04/2026
3	2026-04-15	0	245	525	17.319999999999936	Fechamento 15/04/2026
\.


--
-- Data for Name: movimentacao_estoque; Type: TABLE DATA; Schema: public; Owner: bd_erp_cayube_user
--

COPY public.movimentacao_estoque (id, produto_id, tipo, quantidade, motivo, data) FROM stdin;
\.


--
-- Data for Name: movimento; Type: TABLE DATA; Schema: public; Owner: bd_erp_cayube_user
--

COPY public.movimento (id, tipo, valor, origem, descricao, data) FROM stdin;
1	entrada	126	conta	Injeção de capital para compra de estoque	2026-04-09 16:56:27.120728
2	saida	126	conta	Compra de estoque: Cocada  (36 un.)	2026-04-09 16:56:27.120733
3	entrada	7	conta	Injeção de capital para compra de estoque	2026-04-09 16:57:12.790966
4	saida	7	conta	Compra de estoque: Bala de Banana (2 un.)	2026-04-09 16:57:12.790969
5	entrada	101.5	dinheiro	Injeção de capital para compra de estoque	2026-04-09 16:57:39.335967
6	saida	101.5	dinheiro	Compra de estoque: Cone (29 un.)	2026-04-09 16:57:39.335971
7	entrada	10.5	conta	Injeção de capital para compra de estoque	2026-04-09 16:58:11.308346
8	saida	10.5	conta	Compra de estoque: Quebra-Queixo (3 un.)	2026-04-09 16:58:11.308351
9	entrada	63	conta	Injeção de capital para compra de estoque	2026-04-09 16:58:39.891067
10	saida	63	conta	Compra de estoque: Trufa (18 un.)	2026-04-09 16:58:39.89107
11	entrada	737.79	conta	Saldo em conta corrente ao começo de movimentação do sistema	2026-04-09 17:16:48.432261
12	entrada	14	dinheiro	PAGAMENTO LUCINEIDE ABILITY	2026-04-13 16:51:12.939538
13	entrada	32	conta	PAGAMENTO CLIENTO VIVO	2026-04-13 16:52:17.720624
14	saida	14	dinheiro	Bruna Almoço	2026-04-13 17:05:35.196784
15	entrada	35	dinheiro	Injeção de capital para compra de estoque	2026-04-13 23:32:56.030087
16	saida	35	dinheiro	Compra de estoque: Trufa maracuja (10 un.)	2026-04-13 23:32:56.030092
17	entrada	35	dinheiro	Injeção de capital para compra de estoque	2026-04-13 23:33:32.467153
18	saida	35	dinheiro	Compra de estoque: Trufa Prestigio (10 un.)	2026-04-13 23:33:32.467156
19	entrada	35	conta	Injeção de capital para compra de estoque	2026-04-13 23:33:51.732595
20	saida	35	conta	Compra de estoque: Trufa Brigadeiro (10 un.)	2026-04-13 23:33:51.7326
21	entrada	35	conta	Injeção de capital para compra de estoque	2026-04-13 23:34:12.077861
22	saida	35	conta	Compra de estoque: Cone Maracuja (10 un.)	2026-04-13 23:34:12.077865
23	entrada	35	conta	Injeção de capital para compra de estoque	2026-04-13 23:34:23.781477
24	saida	35	conta	Compra de estoque: Cone Oreo (10 un.)	2026-04-13 23:34:23.781481
25	entrada	35	conta	Injeção de capital para compra de estoque	2026-04-13 23:34:35.038023
26	saida	35	conta	Compra de estoque: Cone beijinho (10 un.)	2026-04-13 23:34:35.038027
27	entrada	35	conta	Injeção de capital para compra de estoque	2026-04-13 23:35:08.384082
28	saida	35	conta	Compra de estoque: Cone Brigadeiro (10 un.)	2026-04-13 23:35:08.384086
29	saida	561.47	conta	Cartão nubank	2026-04-13 23:53:11.784551
30	saida	35	conta	Compra de estoque: COCADA LEITE CONDENSADO (10 un.)	2026-04-15 21:38:48.02274
31	saida	35	conta	Compra de estoque: COCADA SENSAÇÃO (10 un.)	2026-04-15 21:38:48.022745
32	saida	35	conta	Compra de estoque: COCADA MARACUJA (10 un.)	2026-04-15 21:40:46.608571
33	saida	35	conta	Compra de estoque: COCADA CHOCOLATE (10 un.)	2026-04-15 21:40:46.608574
34	saida	35	conta	Compra de estoque: BIJU (PRESTIGIO) (10 un.)	2026-04-15 21:40:46.608576
35	saida	35	conta	Compra de estoque: COCADA AMENDOIM (10 un.)	2026-04-15 21:40:46.608577
36	saida	35	conta	Compra de estoque: COCADA TRADICIONAL COCO QUEIMADO (10 un.)	2026-04-15 21:40:46.608578
37	saida	35	conta	Compra de estoque: COCADA TRADICIONAL BRANCA (10 un.)	2026-04-15 21:40:46.608579
38	entrada	227.5	conta	Injeção de capital para compra de estoque	2026-04-15 21:47:58.701842
39	saida	35	conta	Compra de estoque: TRUFA NINHO (10 un.)	2026-04-15 21:47:58.701847
40	saida	17.5	conta	Compra de estoque: TRUFA MORANGO (5 un.)	2026-04-15 21:47:58.701849
41	saida	17.5	conta	Compra de estoque: Trufa maracuja (5 un.)	2026-04-15 21:47:58.70185
42	saida	17.5	conta	Compra de estoque: CONE NINHO (5 un.)	2026-04-15 21:47:58.701852
43	saida	17.5	conta	Compra de estoque: CONE NINHO (5 un.)	2026-04-15 21:47:58.701854
44	saida	17.5	conta	Compra de estoque: Cone Maracuja (5 un.)	2026-04-15 21:47:58.701855
45	saida	35	conta	Compra de estoque: Bala de Banana (10 un.)	2026-04-15 21:47:58.701857
46	saida	35	conta	Compra de estoque: CARIBE (DOCE DE BANANA C/ CHOCOLATE) (10 un.)	2026-04-15 21:47:58.701858
47	saida	35	conta	Compra de estoque: Quebra-Queixo (10 un.)	2026-04-15 21:47:58.70186
48	entrada	17.5	conta	Injeção de capital para compra de estoque	2026-04-15 21:48:31.022061
49	saida	17.5	conta	Compra de estoque: CONE UVA (5 un.)	2026-04-15 21:48:31.022065
50	saida	3.09	conta	movimento de conta	2026-04-15 22:06:47.831314
51	saida	8	dinheiro	Estorno da venda #118	2026-04-16 16:02:16.331811
52	saida	6	dinheiro	Estorno da venda #130	2026-04-16 20:10:55.52243
53	saida	7	dinheiro	Estorno da venda #129	2026-04-16 20:11:03.775656
54	saida	8	dinheiro	BRUNO	2026-04-17 11:07:27.326775
55	entrada	0	conta	Entrada rápida de estoque - TRUFA MORANGO	2026-04-18 20:09:22.098802
56	entrada	0	dinheiro	Entrada rápida de estoque - Cone Oreo	2026-04-18 20:09:36.090326
57	saida	2	dinheiro	deposito	2026-04-18 20:32:16.280681
58	entrada	2	conta	deposito	2026-04-18 20:32:29.493209
59	saida	0	dinheiro	Entrada rápida de estoque - Cone Maracuja	2026-04-18 20:36:02.698048
60	saida	0	dinheiro	Entrada rápida de estoque - COCADA TRADICIONAL COCO QUEIMADO	2026-04-18 20:38:42.79782
61	saida	0	dinheiro	Entrada rápida de estoque - COCADA MARACUJA	2026-04-18 20:39:09.874539
62	saida	6	dinheiro	saida	2026-04-18 20:51:34.082311
63	saida	0	dinheiro	Entrada rápida de estoque - CARIBE (DOCE DE BANANA C/ CHOCOLATE)	2026-04-20 12:12:06.613014
64	entrada	7	conta	Quitação total do fiado - Cliente: Marcinha vivo	2026-04-20 17:58:35.223328
65	saida	7500	dinheiro	Deposito	2026-04-20 21:34:46.285225
66	entrada	7500	dinheiro	Refazer	2026-04-20 21:35:06.680727
67	saida	75	dinheiro	Deposto	2026-04-20 21:35:18.437103
68	entrada	75	conta	Deposito	2026-04-20 21:35:31.322967
69	saida	10	dinheiro	Racao	2026-04-20 21:35:44.937367
70	saida	20	dinheiro	Mercado	2026-04-20 21:36:27.22668
71	saida	37	conta	Ajuste	2026-04-20 21:37:12.227271
72	entrada	38	conta	Quitação total do fiado - Cliente: Vaguiner Fermino dos Santos	2026-04-21 10:21:02.398887
\.


--
-- Data for Name: movimento_estoque; Type: TABLE DATA; Schema: public; Owner: bd_erp_cayube_user
--

COPY public.movimento_estoque (id, produto_id, tipo, quantidade, motivo, data) FROM stdin;
1	1	entrada	36	Compra	2026-04-09 16:56:27.124326
2	5	entrada	2	Compra	2026-04-09 16:57:12.792787
3	2	entrada	29	Compra	2026-04-09 16:57:39.338018
4	4	entrada	3	Compra	2026-04-09 16:58:11.310234
5	3	entrada	18	Compra	2026-04-09 16:58:39.892948
6	1	saida	1	Venda administrativa	2026-04-09 17:00:07.490254
7	5	saida	1	Venda administrativa	2026-04-09 17:00:28.606682
8	2	saida	1	Venda administrativa	2026-04-09 17:02:02.820558
9	2	saida	1	Venda administrativa	2026-04-09 17:03:22.353554
10	1	saida	1	Venda administrativa	2026-04-09 17:04:06.818956
11	1	saida	1	Venda administrativa	2026-04-09 17:04:30.169519
12	1	saida	1	Venda administrativa	2026-04-09 17:04:49.707999
13	1	saida	1	Venda administrativa	2026-04-09 17:05:07.648249
14	1	saida	1	Venda administrativa	2026-04-09 17:05:27.040852
15	1	saida	2	Venda administrativa	2026-04-09 17:06:39.800789
16	3	saida	1	Venda administrativa	2026-04-09 17:06:52.96041
17	3	saida	1	Venda administrativa	2026-04-09 17:07:11.982123
18	2	saida	1	Venda administrativa	2026-04-09 17:07:32.457139
19	4	saida	1	Venda administrativa	2026-04-09 17:17:39.258601
20	3	saida	1	Venda administrativa	2026-04-09 17:17:51.926395
21	1	saida	1	Venda administrativa	2026-04-09 17:18:03.874228
22	3	saida	1	Venda administrativa	2026-04-09 17:22:03.256299
23	1	saida	1	Venda administrativa	2026-04-09 17:22:21.191018
24	1	saida	1	Venda administrativa	2026-04-09 17:36:55.43835
25	1	saida	2	Venda administrativa	2026-04-09 17:38:26.590017
26	2	saida	3	Venda administrativa	2026-04-09 17:38:53.241553
27	5	saida	1	Venda administrativa	2026-04-09 17:39:23.69301
28	3	saida	2	Venda administrativa	2026-04-09 17:39:39.724648
29	2	saida	3	Venda administrativa	2026-04-09 17:50:32.197175
30	3	saida	1	Venda administrativa	2026-04-09 17:50:45.814579
31	3	entrada	2	Estorno de venda #23	2026-04-09 17:59:56.617788
32	2	entrada	3	Estorno de venda #24	2026-04-09 18:00:16.672145
33	3	entrada	1	Estorno de venda #25	2026-04-09 18:00:45.437414
34	3	saida	2	Venda administrativa	2026-04-09 18:06:01.999652
35	2	saida	3	Venda administrativa	2026-04-09 18:07:50.821791
36	3	saida	1	Venda administrativa	2026-04-09 18:08:15.828162
37	2	saida	1	Venda administrativa	2026-04-09 18:10:45.940891
38	4	saida	1	Venda administrativa	2026-04-09 18:13:01.474592
39	1	saida	1	Venda administrativa	2026-04-09 18:13:34.652236
40	1	saida	1	Venda administrativa	2026-04-09 18:18:02.243111
41	3	saida	1	Venda administrativa	2026-04-09 18:18:28.246987
42	3	saida	1	Venda administrativa	2026-04-09 18:21:41.319473
43	2	saida	6	Venda administrativa	2026-04-09 18:22:03.566194
44	1	saida	3	Venda administrativa	2026-04-09 18:22:27.589089
45	1	saida	3	Venda administrativa	2026-04-09 20:57:55.828418
46	4	entrada	1	Estorno de venda #30	2026-04-09 20:59:54.854776
47	4	saida	1	Venda administrativa	2026-04-09 21:00:31.543048
48	2	entrada	1	Estorno de venda #29	2026-04-09 21:00:51.855835
49	2	saida	1	Venda administrativa	2026-04-09 21:02:07.2433
50	1	saida	2	Uso operacional - PAGOU POR FORA	2026-04-13 16:50:25.190414
51	2	saida	4	Uso operacional - PAGO POR FORA	2026-04-13 16:51:51.686837
52	1	saida	1	Venda administrativa	2026-04-13 16:53:45.218147
53	1	saida	1	Venda administrativa	2026-04-13 16:55:19.11806
54	3	saida	3	Consumo interno	2026-04-13 16:57:28.222733
55	2	saida	6	Consumo interno	2026-04-13 16:57:42.230878
56	3	saida	1	Venda administrativa	2026-04-13 17:00:13.106875
57	3	saida	1	Venda administrativa	2026-04-13 17:01:14.285834
58	2	saida	1	Venda administrativa	2026-04-13 20:35:21.67623
59	2	saida	2	Venda administrativa	2026-04-13 20:36:27.133443
60	1	saida	3	Venda administrativa	2026-04-13 20:37:49.50811
61	1	saida	1	Venda administrativa	2026-04-13 20:38:43.989783
62	1	saida	1	Venda administrativa	2026-04-13 20:39:52.337454
63	3	saida	1	Venda administrativa	2026-04-13 20:40:04.681383
64	1	saida	1	Venda administrativa	2026-04-13 20:40:55.823047
65	3	saida	1	Venda administrativa	2026-04-13 20:41:51.672621
66	4	saida	1	Venda administrativa	2026-04-13 20:43:05.914634
67	1	saida	1	Venda administrativa	2026-04-13 20:43:20.520406
68	1	saida	3	Venda administrativa	2026-04-13 20:44:26.365143
69	3	saida	2	Venda administrativa	2026-04-13 20:44:41.216512
70	1	saida	1	Venda administrativa	2026-04-13 20:45:20.371378
71	8	entrada	10	Compra	2026-04-13 23:32:56.033294
72	9	entrada	10	Compra	2026-04-13 23:33:32.469499
73	10	entrada	10	Compra	2026-04-13 23:33:51.734832
74	11	entrada	10	Compra	2026-04-13 23:34:12.081263
75	12	entrada	10	Compra	2026-04-13 23:34:23.783475
76	13	entrada	10	Compra	2026-04-13 23:34:35.040266
77	14	entrada	10	Compra	2026-04-13 23:35:08.386642
78	9	saida	2	Venda administrativa	2026-04-13 23:36:22.487134
79	10	saida	2	Venda administrativa	2026-04-13 23:36:40.332903
80	8	saida	2	Venda administrativa	2026-04-13 23:37:25.952757
81	9	saida	1	Consumo interno - Benicio	2026-04-13 23:52:12.651766
82	8	saida	2	Pedido aprovado → venda direta (fiado)	2026-04-14 15:15:52.527102
83	9	saida	1	Pedido aprovado → venda direta (fiado)	2026-04-14 15:47:24.029041
84	13	saida	1	Venda administrativa	2026-04-14 15:55:30.59548
85	13	saida	1	Venda administrativa	2026-04-14 15:56:01.789347
86	12	saida	1	Venda administrativa	2026-04-14 15:56:29.623901
87	11	saida	1	Venda administrativa	2026-04-14 16:01:45.208587
88	9	saida	1	Venda administrativa	2026-04-14 16:02:38.308739
89	14	saida	1	Venda administrativa	2026-04-14 16:04:55.994294
90	10	entrada	2	Estorno de venda #58	2026-04-14 16:36:34.71111
91	10	saida	2	Venda direta administrativa	2026-04-14 16:37:03.519274
92	8	saida	1	Venda direta administrativa	2026-04-14 16:45:06.734157
93	12	saida	1	Venda direta administrativa	2026-04-14 16:49:09.817645
94	14	saida	1	Venda direta administrativa	2026-04-14 19:53:00.88033
95	10	saida	1	Venda direta administrativa	2026-04-14 20:02:38.512534
96	11	saida	1	Consumo interno - Bruna	2026-04-14 20:02:57.578813
97	14	saida	1	Venda direta administrativa	2026-04-14 20:08:17.254034
98	9	saida	1	Venda direta administrativa	2026-04-14 20:15:16.509907
99	12	saida	1	Venda direta administrativa	2026-04-14 20:17:03.016522
100	10	saida	1	Consumo interno - Benicio	2026-04-14 20:19:17.07874
101	11	saida	1	Venda direta administrativa	2026-04-14 20:44:14.652824
102	10	saida	1	Venda direta administrativa	2026-04-14 20:45:02.665281
103	13	saida	1	Venda direta administrativa	2026-04-14 22:39:10.645228
104	9	saida	2	Venda direta administrativa	2026-04-14 22:39:45.958497
105	9	saida	1	Venda direta administrativa	2026-04-14 22:40:18.236737
106	13	saida	1	Venda direta administrativa	2026-04-14 22:40:36.578609
107	8	saida	1	Venda direta administrativa	2026-04-14 22:42:56.327514
108	13	saida	1	Venda direta administrativa	2026-04-14 22:43:47.65545
109	13	saida	1	Venda direta administrativa	2026-04-14 22:45:09.342957
110	11	saida	1	Venda direta administrativa	2026-04-14 22:46:11.924833
111	10	saida	1	Venda direta administrativa	2026-04-14 22:46:48.621072
112	10	saida	1	Venda direta administrativa	2026-04-14 22:49:42.301139
113	12	saida	1	Venda direta administrativa	2026-04-14 22:50:53.545942
114	11	saida	1	Venda direta administrativa	2026-04-14 22:52:04.130138
115	12	saida	1	Venda direta administrativa	2026-04-14 22:52:57.056244
116	14	saida	1	Venda direta administrativa	2026-04-14 22:55:06.341934
117	14	saida	1	Venda direta administrativa	2026-04-14 22:56:23.224702
118	12	saida	2	Venda direta administrativa	2026-04-14 22:57:41.765142
119	8	saida	1	Venda direta administrativa	2026-04-14 22:58:50.4369
120	10	saida	1	Venda direta administrativa	2026-04-14 23:00:13.643324
121	8	saida	2	Venda direta administrativa	2026-04-14 23:02:59.019347
122	14	saida	2	Venda direta administrativa	2026-04-14 23:03:33.615703
123	14	saida	1	Venda direta administrativa	2026-04-14 23:04:23.915143
124	10	saida	1	Venda direta administrativa	2026-04-14 23:04:55.819452
125	14	saida	1	Venda direta administrativa	2026-04-14 23:05:27.011506
126	11	saida	2	Consumo interno - Caio e Yuri	2026-04-14 23:06:21.291652
127	18	entrada	10	Compra	2026-04-15 21:38:48.026457
128	17	entrada	10	Compra	2026-04-15 21:38:48.02646
129	21	entrada	10	Compra	2026-04-15 21:40:46.613144
130	24	entrada	10	Compra	2026-04-15 21:40:46.613149
131	19	entrada	10	Compra	2026-04-15 21:40:46.613151
132	25	entrada	10	Compra	2026-04-15 21:40:46.613153
133	16	entrada	10	Compra	2026-04-15 21:40:46.613183
134	15	entrada	10	Compra	2026-04-15 21:40:46.613187
135	27	entrada	10	Compra	2026-04-15 21:47:58.706386
136	28	entrada	5	Compra	2026-04-15 21:47:58.70639
137	8	entrada	5	Compra	2026-04-15 21:47:58.706391
138	29	entrada	5	Compra	2026-04-15 21:47:58.706392
139	29	entrada	5	Compra	2026-04-15 21:47:58.706393
140	11	entrada	5	Compra	2026-04-15 21:47:58.706394
141	5	entrada	10	Compra	2026-04-15 21:47:58.706396
142	20	entrada	10	Compra	2026-04-15 21:47:58.706397
143	4	entrada	10	Compra	2026-04-15 21:47:58.706398
144	30	entrada	5	Compra	2026-04-15 21:48:31.024624
145	4	saida	5	Venda direta administrativa	2026-04-15 21:49:25.262706
146	18	saida	2	Venda direta administrativa	2026-04-15 21:50:47.693775
147	25	saida	1	Venda direta administrativa	2026-04-15 21:50:47.702669
148	15	saida	1	Venda direta administrativa	2026-04-15 21:50:47.710973
149	16	saida	2	Venda direta administrativa	2026-04-15 21:50:47.723696
150	20	saida	3	Venda direta administrativa	2026-04-15 21:58:49.482609
151	4	saida	1	Venda direta administrativa	2026-04-15 21:58:49.491119
152	16	saida	1	Venda direta administrativa	2026-04-15 21:58:49.496797
153	5	saida	1	Venda direta administrativa	2026-04-15 21:58:49.503873
154	9	saida	1	Consumo interno - Benicio	2026-04-15 22:04:03.77265
155	8	saida	1	Perda - Faltou no pedido	2026-04-15 22:04:36.254691
156	12	saida	1	Consumo interno - Yuri	2026-04-15 22:04:56.721506
157	27	saida	1	Consumo interno - Caio	2026-04-15 22:05:11.396801
158	13	saida	1	Consumo interno - Bruno	2026-04-16 15:27:19.718903
159	4	saida	2	Venda direta administrativa	2026-04-16 15:28:06.643381
160	19	saida	2	Venda direta administrativa	2026-04-16 15:28:55.638019
161	18	saida	1	Venda direta administrativa	2026-04-16 15:28:55.760448
162	16	saida	2	Venda direta administrativa	2026-04-16 15:29:54.702012
163	29	saida	1	Venda direta administrativa	2026-04-16 15:29:54.709875
164	14	saida	1	Venda direta administrativa	2026-04-16 15:29:54.721643
165	20	saida	1	Venda direta administrativa	2026-04-16 15:30:53.536753
166	20	saida	1	Venda direta administrativa	2026-04-16 15:50:07.170654
167	11	saida	1	Venda direta administrativa	2026-04-16 15:54:27.343661
168	28	saida	1	Venda direta administrativa	2026-04-16 15:58:52.692331
169	28	saida	1	Venda direta administrativa	2026-04-16 15:59:16.846505
170	12	saida	1	Venda direta administrativa	2026-04-16 16:01:25.000681
171	11	entrada	1	Estorno de venda #118	2026-04-16 16:02:16.334211
172	11	saida	1	Venda direta administrativa	2026-04-16 16:02:34.218321
173	20	saida	1	Venda direta administrativa	2026-04-16 17:32:24.259056
174	29	saida	1	Venda direta administrativa	2026-04-16 19:12:34.615778
175	10	saida	1	Venda direta administrativa	2026-04-16 20:09:11.932964
176	8	saida	1	Venda direta administrativa	2026-04-16 20:09:11.944522
177	27	saida	1	Venda direta administrativa	2026-04-16 20:09:44.514439
178	25	saida	1	Venda direta administrativa	2026-04-16 20:09:44.524645
179	25	saida	1	Venda direta administrativa	2026-04-16 20:10:22.552922
180	27	saida	1	Venda direta administrativa	2026-04-16 20:10:22.565826
181	27	entrada	1	Estorno de venda #130	2026-04-16 20:10:55.524432
182	25	entrada	1	Estorno de venda #129	2026-04-16 20:11:03.777418
183	25	saida	1	Venda direta administrativa	2026-04-16 20:11:50.138845
184	27	saida	1	Venda direta administrativa	2026-04-16 20:11:50.148344
185	15	saida	1	Venda direta administrativa	2026-04-16 20:17:06.85351
186	30	saida	1	Venda direta administrativa	2026-04-16 20:17:58.497886
187	18	saida	1	Venda direta administrativa	2026-04-16 20:18:46.882506
188	20	entrada	1	Estorno de venda #117	2026-04-16 20:49:22.900916
189	21	saida	1	Venda direta administrativa	2026-04-17 10:30:29.518481
190	20	saida	1	Venda administrativa	2026-04-17 14:57:38.795063
191	16	saida	1	Venda administrativa	2026-04-17 14:58:50.029202
192	20	saida	1	Venda administrativa	2026-04-17 14:59:09.162465
193	20	saida	1	Venda administrativa	2026-04-17 15:41:25.740507
194	21	saida	1	Venda administrativa	2026-04-17 15:41:52.407595
195	19	saida	3	Venda administrativa	2026-04-17 15:50:05.782485
196	5	saida	1	Venda administrativa	2026-04-17 16:00:11.72518
197	29	saida	1	Venda administrativa	2026-04-17 17:29:55.448334
198	11	saida	1	Venda administrativa	2026-04-17 17:30:09.367256
199	29	saida	1	Venda administrativa	2026-04-17 17:30:23.815642
200	19	saida	1	Venda administrativa	2026-04-17 17:30:44.272243
201	11	saida	1	Pedido cliente aprovado + PIX confirmado	2026-04-17 18:05:50.384998
202	29	saida	1	Pedido cliente aprovado + PIX confirmado	2026-04-17 18:05:55.10665
203	18	saida	1	Venda rápida	2026-04-17 18:08:54.927608
204	5	saida	1	Venda administrativa	2026-04-17 18:27:23.913649
205	18	entrada	1	Cancelamento da venda #148	2026-04-17 18:47:47.544143
206	18	saida	1	Venda rápida	2026-04-17 18:48:20.32901
207	5	saida	1	Venda rápida	2026-04-17 18:51:40.225382
208	18	saida	1	Venda rápida	2026-04-17 18:51:40.225386
209	21	saida	1	Venda administrativa	2026-04-17 18:52:13.455969
210	5	saida	1	Venda rápida	2026-04-17 18:55:24.467474
211	17	saida	1	Venda rápida	2026-04-17 18:55:24.467479
212	18	saida	1	Venda rápida	2026-04-17 18:56:02.357686
213	25	saida	1	Venda rápida	2026-04-17 18:56:46.484485
214	4	saida	1	Venda rápida	2026-04-17 18:57:25.843216
215	16	saida	1	Venda administrativa	2026-04-18 12:34:03.796152
216	16	saida	1	Pedido cliente aprovado + PIX confirmado	2026-04-18 13:45:10.095226
217	27	saida	1	Caio	2026-04-18 14:32:05.125641
218	11	saida	1	Perda Quebrado	2026-04-18 14:32:20.825871
219	28	saida	1	Perda Quebrado	2026-04-18 14:32:37.502733
220	28	entrada	1	Entrada rápida	2026-04-18 20:09:22.102649
221	12	entrada	1	Entrada rápida	2026-04-18 20:09:36.093352
222	13	saida	1	BRUNA	2026-04-18 20:24:01.60908
223	11	entrada	1	Entrada rápida	2026-04-18 20:36:02.701031
224	16	entrada	1	Entrada rápida	2026-04-18 20:38:42.800709
225	21	entrada	1	Entrada rápida	2026-04-18 20:39:09.877485
226	20	saida	1	invetario	2026-04-18 20:47:57.873333
227	28	saida	1	perda	2026-04-18 21:12:10.590149
228	27	saida	1	perda	2026-04-18 21:12:21.139222
229	11	saida	1	perda	2026-04-18 21:12:52.94788
230	12	saida	1	Pwrda	2026-04-18 23:48:30.053911
231	20	entrada	1	Entrada rápida	2026-04-20 12:12:06.617017
232	19	saida	1	Bruna	2026-04-20 15:06:06.759738
233	24	saida	1	Caio	2026-04-20 15:06:29.182175
234	27	saida	1	BENICIO	2026-04-20 17:36:31.856946
235	30	saida	1	YURI	2026-04-20 17:36:42.358528
\.


--
-- Data for Name: notificacao; Type: TABLE DATA; Schema: public; Owner: bd_erp_cayube_user
--

COPY public.notificacao (id, tipo, mensagem, lida, data) FROM stdin;
7	venda	Venda direta lançada para Renato da Silva Pereira - Bala de Banana (1 un.)	t	2026-04-17 16:00:11.746388
5	venda	Venda direta lançada para Jhordan Rodrigues de Sales - COCADA MARACUJA (1 un.)	t	2026-04-17 15:41:52.428904
3	venda	Venda direta lançada para João Maria de Almeida - CARIBE (DOCE DE BANANA C/ CHOCOLATE) (1 un.)	t	2026-04-17 14:59:09.178884
4	venda	Venda direta lançada para Jhordan Rodrigues de Sales - CARIBE (DOCE DE BANANA C/ CHOCOLATE) (1 un.)	t	2026-04-17 15:41:25.830074
6	venda	Venda direta lançada para Wellington Cunha Gregorio - BIJU (PRESTIGIO) (3 un.)	t	2026-04-17 15:50:05.833923
2	venda	Venda direta lançada para João Maria de Almeida - COCADA TRADICIONAL COCO QUEIMADO (1 un.)	t	2026-04-17 14:58:50.046844
1	venda	Venda direta lançada para Edvaldo Rodrigues Galvão - CARIBE (DOCE DE BANANA C/ CHOCOLATE) (1 un.)	t	2026-04-17 14:57:38.831676
11	venda	Venda direta lançada para Roni Araujo dos Santos - BIJU (PRESTIGIO) (1 un.)	t	2026-04-17 17:30:44.290554
10	venda	Venda direta lançada para Roni Araujo dos Santos - CONE NINHO (1 un.)	t	2026-04-17 17:30:23.836198
9	venda	Venda direta lançada para Evandro Alves Pereira - Cone Maracuja (1 un.)	t	2026-04-17 17:30:09.38743
8	venda	Venda direta lançada para Evandro Alves Pereira - CONE NINHO (1 un.)	t	2026-04-17 17:29:55.468794
\.


--
-- Data for Name: produto; Type: TABLE DATA; Schema: public; Owner: bd_erp_cayube_user
--

COPY public.produto (id, nome, preco, custo, estoque) FROM stdin;
14	Cone Brigadeiro	8	3.5	0
8	Trufa maracuja	6	3.5	0
4	Quebra-Queixo	9	3.5	0
2	Cone	8	3.5	0
10	Trufa Brigadeiro	6	3.5	0
28	TRUFA MORANGO	6	3.5	0
3	Trufa	6	3.5	0
1	Cocada 	7	3.5	0
16	COCADA TRADICIONAL COCO QUEIMADO	7	3.5	0
22	COCADA RECHEADA DOCE DE ABOBORA	7	3.5	0
23	COCADA ABACAXI	7	3.5	0
26	DOCE DE LEITE COM COCO	7	3.5	0
11	Cone Maracuja	8	3.5	0
12	Cone Oreo	8	3.5	0
13	Cone beijinho	8	3.5	0
20	CARIBE (DOCE DE BANANA C/ CHOCOLATE)	7	3.5	0
19	BIJU (PRESTIGIO)	7	3.5	0
29	CONE NINHO	8	3.5	0
27	TRUFA NINHO	6	3.5	0
30	CONE UVA	8	3.5	0
18	COCADA LEITE CONDENSADO	7	3.5	0
25	COCADA AMENDOIM	7	3.5	3
17	COCADA SENSAÇÃO	7	3.5	7
5	Bala de Banana	6	3.5	0
21	COCADA MARACUJA	7	3.5	2
15	COCADA TRADICIONAL BRANCA	7	3.5	2
9	Trufa Prestigio	6	3.5	0
24	COCADA CHOCOLATE	7	3.5	6
\.


--
-- Data for Name: saldo; Type: TABLE DATA; Schema: public; Owner: bd_erp_cayube_user
--

COPY public.saldo (id, dinheiro, conta) FROM stdin;
1	0	266.2299999999999
\.


--
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: bd_erp_cayube_user
--

COPY public.usuario (id, nome, usuario, senha, nivel) FROM stdin;
1	Administrador	admin	scrypt:32768:8:1$Cbxoywm3YDFplDZS$80b495411b2c6a1e6e90529b7aaec0dc99c00724ebcbbbaf6d7262d2cd06a69814505ea3fccad5d5402dee70e85deca0fc7a3609b4e4d2e4de14795d14ba3bdd	admin
2	Bruna Rafaela Soares Silva	Bruna	scrypt:32768:8:1$fGZI3r0rBJSmDkob$e67e0c3143427e6832cd8e12bd3aeb11ec5e29db87a231bd4a12928057f8db0e6178797c548ee58bf90d5029f6b2c54611536420080752b4fd7852acfc3f8f12	admin
3	Caio Henrique Soares Silva	Caio	scrypt:32768:8:1$5afZe7g41HVakbmM$5c94248d9ab94c49b3a6690d319f9449b13e3a7d8eb872593e08d4f9e6494667edeb7ad7f24bf6c39719a203632c564bf9de87d4b02e23944a6b27253f4d0ae1	funcionario
\.


--
-- Data for Name: venda; Type: TABLE DATA; Schema: public; Owner: bd_erp_cayube_user
--

COPY public.venda (id, produto_id, cliente_id, quantidade, total, pago, forma_pagamento, data, status_pedido, status_pix) FROM stdin;
1	1	19	1	7	f	fiado	2026-04-09 17:00:07.493644	aprovado	pendente
2	5	19	1	6	f	fiado	2026-04-09 17:00:28.609521	aprovado	pendente
3	2	25	1	8	f	fiado	2026-04-09 17:02:02.823268	aprovado	pendente
4	2	9	1	8	f	fiado	2026-04-09 17:03:22.356148	aprovado	pendente
5	1	5	1	7	f	fiado	2026-04-09 17:04:06.82193	aprovado	pendente
6	1	5	1	7	f	fiado	2026-04-09 17:04:30.172077	aprovado	pendente
7	1	5	1	7	f	fiado	2026-04-09 17:04:49.710932	aprovado	pendente
8	1	5	1	7	f	fiado	2026-04-09 17:05:07.650965	aprovado	pendente
9	1	5	1	7	f	fiado	2026-04-09 17:05:27.049694	aprovado	pendente
10	1	23	2	14	f	fiado	2026-04-09 17:06:39.803587	aprovado	pendente
12	3	23	1	6	f	fiado	2026-04-09 17:07:11.984884	aprovado	pendente
13	2	23	1	8	f	fiado	2026-04-09 17:07:32.45968	aprovado	pendente
11	3	4	1	6	t	transferencia	2026-04-09 17:06:52.963698	aprovado	pago
14	4	11	1	9	f	fiado	2026-04-09 17:17:39.262455	aprovado	pendente
15	3	11	1	6	f	fiado	2026-04-09 17:17:51.929132	aprovado	pendente
16	1	11	1	7	f	fiado	2026-04-09 17:18:03.894808	aprovado	pendente
17	3	26	1	6	f	fiado	2026-04-09 17:22:03.259293	aprovado	pendente
18	1	26	1	7	f	fiado	2026-04-09 17:22:21.193635	aprovado	pendente
19	1	23	1	7	f	fiado	2026-04-09 17:36:55.441046	aprovado	pendente
20	1	24	2	14	f	fiado	2026-04-09 17:38:26.592722	aprovado	pendente
21	2	24	3	24	f	fiado	2026-04-09 17:38:53.244418	aprovado	pendente
22	5	24	1	6	f	fiado	2026-04-09 17:39:23.699971	aprovado	pendente
26	3	24	2	12	f	fiado	2026-04-09 18:06:02.005071	aprovado	pendente
27	2	27	3	24	f	fiado	2026-04-09 18:07:50.826309	aprovado	pendente
28	3	27	1	6	f	fiado	2026-04-09 18:08:15.832863	aprovado	pendente
31	1	29	1	7	f	fiado	2026-04-09 18:13:34.657255	aprovado	pendente
32	1	30	1	7	f	fiado	2026-04-09 18:18:02.249163	aprovado	pendente
33	3	30	1	6	f	fiado	2026-04-09 18:18:28.251535	aprovado	pendente
34	3	18	1	6	f	fiado	2026-04-09 18:21:41.323783	aprovado	pendente
35	2	18	6	48	f	fiado	2026-04-09 18:22:03.571545	aprovado	pendente
36	1	18	3	21	f	fiado	2026-04-09 18:22:27.593968	aprovado	pendente
37	1	31	3	21	f	fiado	2026-04-09 20:57:55.911909	aprovado	pendente
38	4	29	1	9	f	fiado	2026-04-09 21:00:31.550491	aprovado	pendente
39	2	28	1	8	f	fiado	2026-04-09 21:02:07.247363	aprovado	pendente
40	1	22	1	7	f	fiado	2026-04-13 16:53:45.223172	venda_direta	pendente
41	1	32	1	7	f	fiado	2026-04-13 16:55:19.122293	venda_direta	pendente
42	3	33	1	6	f	fiado	2026-04-13 17:00:13.117017	venda_direta	pendente
45	2	36	2	16	f	fiado	2026-04-13 20:36:27.137156	venda_direta	pendente
46	1	37	3	21	f	fiado	2026-04-13 20:37:49.516769	venda_direta	pendente
47	1	38	1	7	f	fiado	2026-04-13 20:38:43.999204	venda_direta	pendente
50	1	40	1	7	f	fiado	2026-04-13 20:40:55.826833	venda_direta	pendente
51	3	41	1	6	f	fiado	2026-04-13 20:41:51.677181	venda_direta	pendente
52	4	42	1	9	f	fiado	2026-04-13 20:43:05.921288	venda_direta	pendente
53	1	42	1	7	f	fiado	2026-04-13 20:43:20.52426	venda_direta	pendente
54	1	43	3	21	f	fiado	2026-04-13 20:44:26.369358	venda_direta	pendente
55	3	43	2	12	f	fiado	2026-04-13 20:44:41.220203	venda_direta	pendente
56	1	44	1	7	f	fiado	2026-04-13 20:45:20.37623	venda_direta	pendente
57	9	45	2	12	f	fiado	2026-04-13 23:36:22.491672	venda_direta	pendente
59	8	45	2	12	f	fiado	2026-04-13 23:37:25.959632	venda_direta	pendente
60	8	33	2	12	f	fiado	2026-04-14 15:15:21.500488	venda_direta	pendente
61	9	33	1	6	f	fiado	2026-04-14 15:22:05.959776	venda_direta	pendente
63	13	4	1	8	f	fiado	2026-04-14 15:56:01.793844	venda_direta	pendente
64	12	4	1	8	f	fiado	2026-04-14 15:56:29.631186	venda_direta	pendente
65	11	24	1	8	f	fiado	2026-04-14 16:01:45.214487	venda_direta	pendente
66	9	30	1	6	f	fiado	2026-04-14 16:02:38.312542	venda_direta	pendente
67	14	27	1	8	f	fiado	2026-04-14 16:04:55.998266	venda_direta	pendente
68	10	45	2	12	f	fiado	2026-04-14 16:37:03.52501	venda_direta	pendente
69	8	24	1	6	f	fiado	2026-04-14 16:45:06.802151	venda_direta	pendente
70	12	20	1	8	t	transferencia	2026-04-14 16:49:09.820276	venda_direta	pago
71	14	12	1	8	f	fiado	2026-04-14 19:53:00.885146	venda_direta	pendente
72	10	7	1	6	f	fiado	2026-04-14 20:02:38.516295	venda_direta	pendente
73	14	17	1	8	f	fiado	2026-04-14 20:08:17.258099	venda_direta	pendente
74	9	47	1	6	t	pix	2026-04-14 20:15:16.516634	venda_direta	pago
75	12	48	1	8	f	fiado	2026-04-14 20:17:03.115891	venda_direta	pendente
77	10	51	1	6	t	pix	2026-04-14 20:45:02.716929	venda_direta	pago
76	11	50	1	8	t	transferencia	2026-04-14 20:44:14.664397	venda_direta	pago
78	13	52	1	8	t	pix	2026-04-14 22:39:10.653009	venda_direta	pago
79	9	52	2	12	t	pix	2026-04-14 22:39:45.964374	venda_direta	pago
82	8	53	1	6	t	pix	2026-04-14 22:42:56.419199	venda_direta	pago
83	13	54	1	8	t	pix	2026-04-14 22:43:47.661464	venda_direta	pago
84	13	55	1	8	t	pix	2026-04-14 22:45:09.350832	venda_direta	pago
85	11	56	1	8	f	fiado	2026-04-14 22:46:11.928748	venda_direta	pendente
86	10	56	1	6	f	fiado	2026-04-14 22:46:48.62513	venda_direta	pendente
87	10	58	1	6	f	fiado	2026-04-14 22:49:42.344459	venda_direta	pendente
88	12	59	1	8	f	fiado	2026-04-14 22:50:53.549851	venda_direta	pendente
89	11	60	1	8	f	fiado	2026-04-14 22:52:04.135819	venda_direta	pendente
90	12	61	1	8	f	fiado	2026-04-14 22:52:57.060231	venda_direta	pendente
91	14	62	1	8	f	fiado	2026-04-14 22:55:06.348677	venda_direta	pendente
92	14	63	1	8	f	fiado	2026-04-14 22:56:23.229131	venda_direta	pendente
93	12	64	2	16	f	fiado	2026-04-14 22:57:41.77191	venda_direta	pendente
94	8	65	1	6	f	fiado	2026-04-14 22:58:50.440787	venda_direta	pendente
49	3	39	1	6	t	transferencia	2026-04-13 20:40:04.685376	venda_direta	pago
81	13	52	1	8	t	transferencia	2026-04-14 22:40:36.58254	venda_direta	pago
43	3	34	1	6	t	transferencia	2026-04-13 17:01:14.29235	venda_direta	pago
80	9	52	1	6	t	transferencia	2026-04-14 22:40:18.241533	venda_direta	pago
62	13	46	1	8	t	transferencia	2026-04-14 15:55:30.599714	venda_direta	pago
96	8	67	2	12	f	fiado	2026-04-14 23:02:59.023414	venda_direta	pendente
98	14	71	1	8	f	fiado	2026-04-14 23:04:23.920716	venda_direta	pendente
100	14	70	1	8	f	fiado	2026-04-14 23:05:27.017685	venda_direta	pendente
48	1	39	1	7	t	transferencia	2026-04-13 20:39:52.342346	venda_direta	pago
101	4	72	5	45	f	fiado	2026-04-15 21:49:25.26774	venda_direta	pendente
102	18	45	2	14	f	fiado	2026-04-15 21:50:47.697643	venda_direta	pendente
103	25	45	1	7	f	fiado	2026-04-15 21:50:47.706271	venda_direta	pendente
104	15	45	1	7	f	fiado	2026-04-15 21:50:47.714575	venda_direta	pendente
105	16	45	2	14	f	fiado	2026-04-15 21:50:47.727741	venda_direta	pendente
106	20	74	3	21	f	fiado	2026-04-15 21:58:49.487156	venda_direta	pendente
107	4	74	1	9	f	fiado	2026-04-15 21:58:49.493678	venda_direta	pendente
108	16	74	1	7	f	fiado	2026-04-15 21:58:49.499276	venda_direta	pendente
109	5	74	1	6	f	fiado	2026-04-15 21:58:49.5062	venda_direta	pendente
110	4	11	2	18	f	fiado	2026-04-16 15:28:06.648071	venda_direta	pendente
111	19	8	2	14	t	dinheiro	2026-04-16 15:28:55.722857	venda_direta	pago
112	18	8	1	7	t	dinheiro	2026-04-16 15:28:55.900568	venda_direta	pago
116	20	18	1	7	f	fiado	2026-04-16 15:30:53.59361	venda_direta	pendente
119	28	7	1	6	f	fiado	2026-04-16 15:58:52.697085	venda_direta	pendente
120	28	9	1	6	f	fiado	2026-04-16 15:59:16.849931	venda_direta	pendente
121	12	75	1	8	f	fiado	2026-04-16 16:01:25.004178	venda_direta	pendente
122	11	24	1	8	f	fiado	2026-04-16 16:02:34.22166	venda_direta	pendente
123	20	15	1	7	f	fiado	2026-04-16 17:32:24.26685	venda_direta	pendente
124	29	28	1	8	f	fiado	2026-04-16 19:12:34.622594	venda_direta	pendente
125	10	30	1	6	f	fiado	2026-04-16 20:09:11.938155	venda_direta	pendente
126	8	30	1	6	f	fiado	2026-04-16 20:09:11.947895	venda_direta	pendente
131	25	5	1	7	f	fiado	2026-04-16 20:11:50.14253	venda_direta	pendente
132	27	5	1	6	f	fiado	2026-04-16 20:11:50.15191	venda_direta	pendente
134	30	28	1	8	f	fiado	2026-04-16 20:17:58.501286	venda_direta	pendente
135	18	12	1	7	f	fiado	2026-04-16 20:18:46.88768	venda_direta	pendente
95	10	66	1	6	t	transferencia	2026-04-14 23:00:13.647205	venda_direta	pago
136	21	76	1	7	t	dinheiro	2026-04-17 10:30:29.528331	venda_direta	pago
137	20	15	1	7	f	fiado	2026-04-17 14:57:38.805649	aprovado	pendente
138	16	29	1	7	f	fiado	2026-04-17 14:58:50.033875	aprovado	pendente
139	20	29	1	7	f	fiado	2026-04-17 14:59:09.166798	aprovado	pendente
140	20	18	1	7	f	fiado	2026-04-17 15:41:25.746929	aprovado	pendente
141	21	18	1	7	f	fiado	2026-04-17 15:41:52.4139	aprovado	pendente
142	19	4	3	21	f	fiado	2026-04-17 15:50:05.813783	aprovado	pendente
143	5	9	1	6	f	fiado	2026-04-17 16:00:11.730501	aprovado	pendente
146	29	30	1	8	f	fiado	2026-04-17 17:30:23.823577	aprovado	pendente
147	19	30	1	7	f	fiado	2026-04-17 17:30:44.277383	aprovado	pendente
145	11	75	1	8	t	pix	2026-04-17 17:30:09.374686	aprovado	pago
144	29	75	1	8	t	pix	2026-04-17 17:29:55.454497	aprovado	pago
149	5	24	1	6	f	fiado	2026-04-17 18:27:23.921239	aprovado	pendente
150	18	4	1	7	f	fiado	2026-04-17 18:48:20.335204	aprovado	pendente
151	5	52	1	6	t	pix	2026-04-17 18:51:40.238187	aprovado	pago
152	18	52	1	7	t	pix	2026-04-17 18:51:40.238192	aprovado	pago
153	21	56	1	7	f	fiado	2026-04-17 18:52:13.460721	aprovado	pendente
154	5	78	1	6	f	fiado	2026-04-17 18:55:24.476175	aprovado	pendente
155	17	78	1	7	f	fiado	2026-04-17 18:55:24.47618	aprovado	pendente
157	25	80	1	7	f	fiado	2026-04-17 18:56:46.490513	aprovado	pendente
158	4	81	1	9	f	fiado	2026-04-17 18:57:25.914009	aprovado	pendente
168	11	85	1	8	t	dinheiro	2026-04-18 14:28:57.721381	aprovado	pendente
160	16	35	1	7	t	pix	2026-04-18 13:31:32.158864	aprovado	pago
133	15	35	1	7	t	transferencia	2026-04-16 20:17:06.857101	venda_direta	pago
173	20	31	1	7	f	fiado	2026-04-18 14:30:18.606009	aprovado	pendente
171	27	88	1	6	f	fiado	2026-04-18 14:30:06.19695	aprovado	pendente
170	29	87	1	8	f	fiado	2026-04-18 14:29:39.51149	aprovado	pendente
169	13	86	1	8	f	fiado	2026-04-18 14:29:21.476475	aprovado	pendente
164	13	83	1	8	f	fiado	2026-04-18 14:14:19.329744	aprovado	pendente
166	8	89	1	6	t	dinheiro	2026-04-18 14:28:13.250175	aprovado	pendente
163	21	83	1	7	f	fiado	2026-04-18 14:14:19.329737	aprovado	pendente
162	29	82	1	8	f	fiado	2026-04-18 14:13:00.782246	aprovado	pendente
161	21	82	1	7	f	fiado	2026-04-18 14:12:41.823209	aprovado	pendente
172	28	88	1	6	f	fiado	2026-04-18 14:30:06.196956	aprovado	pendente
167	12	84	1	8	f	fiado	2026-04-18 14:28:33.966734	aprovado	pendente
99	10	69	1	6	t	transferencia	2026-04-14 23:04:55.823513	venda_direta	pago
156	18	79	1	7	t	transferencia	2026-04-17 18:56:02.362424	aprovado	pago
97	14	68	2	16	t	transferencia	2026-04-14 23:03:33.619398	venda_direta	pago
128	25	4	1	7	t	transferencia	2026-04-16 20:09:44.528341	venda_direta	pago
127	27	4	1	6	t	transferencia	2026-04-16 20:09:44.51823	venda_direta	pago
113	16	46	2	14	t	transferencia	2026-04-16 15:29:54.705537	venda_direta	pago
114	29	46	1	8	t	transferencia	2026-04-16 15:29:54.713262	venda_direta	pago
115	14	46	1	8	t	transferencia	2026-04-16 15:29:54.725461	venda_direta	pago
44	2	35	1	8	t	transferencia	2026-04-13 20:35:21.733367	venda_direta	pago
229	21	106	1	7	t	dinheiro	2026-04-19 00:06:00.916096	venda_direta	pago
227	15	104	1	7	t	transferencia	2026-04-18 23:50:34.028422	venda_direta	pago
228	25	105	1	7	t	transferencia	2026-04-18 23:50:45.822114	venda_direta	pago
176	5	90	1	6	f	fiado	2026-04-18 14:31:22.680196	aprovado	pendente
175	15	90	1	7	f	fiado	2026-04-18 14:31:22.68019	aprovado	pendente
174	21	3	1	7	f	fiado	2026-04-18 14:30:31.064335	aprovado	pendente
215	17	101	1	7	f	fiado	2026-04-18 20:44:28.64921	aprovado	pendente
214	24	101	1	7	f	fiado	2026-04-18 20:44:28.649209	aprovado	pendente
213	24	101	1	7	f	fiado	2026-04-18 20:44:28.649207	aprovado	pendente
212	19	101	1	7	f	fiado	2026-04-18 20:44:28.649206	aprovado	pendente
211	4	101	1	9	f	fiado	2026-04-18 20:44:28.649201	recusado	cancelado
210	8	93	1	6	t	dinheiro	2026-04-18 20:43:33.105755	recusado	cancelado
209	16	93	1	7	t	dinheiro	2026-04-18 20:43:33.105753	recusado	cancelado
208	8	93	1	6	t	dinheiro	2026-04-18 20:43:33.105748	recusado	cancelado
196	5	19	1	6	t	dinheiro	2026-04-18 20:28:50.03501	recusado	cancelado
201	19	95	1	7	t	dinheiro	2026-04-18 20:29:27.996393	aprovado	pendente
200	8	94	1	6	t	pix	2026-04-18 20:29:16.3436	aprovado	pendente
199	15	94	1	7	t	pix	2026-04-18 20:29:16.343594	aprovado	pendente
195	18	92	1	7	t	pix	2026-04-18 20:28:30.074359	recusado	cancelado
194	15	91	1	7	t	dinheiro	2026-04-18 20:28:04.899442	recusado	cancelado
216	18	101	1	7	f	fiado	2026-04-18 20:44:28.649211	aprovado	pendente
217	16	39	1	7	t	pix	2026-04-18 23:16:45.281645	venda_direta	pago
218	16	39	1	7	t	pix	2026-04-18 23:16:45.281651	venda_direta	pago
219	25	103	1	7	t	dinheiro	2026-04-18 23:44:41.773195	venda_direta	pago
220	19	103	1	7	t	dinheiro	2026-04-18 23:44:41.773198	venda_direta	pago
224	15	102	1	7	f	fiado	2026-04-18 23:47:57.299442	venda_direta	pendente
225	11	102	1	8	f	fiado	2026-04-18 23:47:57.299447	venda_direta	pendente
226	27	102	1	6	f	fiado	2026-04-18 23:47:57.299449	venda_direta	pendente
193	21	91	1	7	t	dinheiro	2026-04-18 20:28:04.89944	recusado	cancelado
192	27	91	1	6	t	dinheiro	2026-04-18 20:28:04.899438	recusado	cancelado
191	28	91	1	6	t	dinheiro	2026-04-18 20:28:04.899432	recusado	cancelado
190	15	56	1	7	f	fiado	2026-04-18 20:26:44.287902	recusado	cancelado
189	29	99	1	8	f	fiado	2026-04-18 20:26:26.913628	recusado	cancelado
188	29	99	1	8	f	fiado	2026-04-18 20:26:26.913625	recusado	cancelado
187	29	99	1	8	f	fiado	2026-04-18 20:26:26.913619	recusado	cancelado
186	11	60	1	8	f	fiado	2026-04-18 20:26:03.745518	recusado	cancelado
185	11	100	1	8	f	fiado	2026-04-18 20:25:53.081765	recusado	cancelado
184	30	78	1	8	f	fiado	2026-04-18 20:25:14.251223	recusado	cancelado
183	30	58	1	8	f	fiado	2026-04-18 20:25:03.820644	recusado	cancelado
182	5	97	1	6	f	fiado	2026-04-18 20:24:49.010105	recusado	cancelado
181	5	96	1	6	f	fiado	2026-04-18 20:24:38.530296	recusado	cancelado
180	5	19	1	6	f	fiado	2026-04-18 20:11:09.717409	recusado	cancelado
230	20	31	1	7	f	fiado	2026-04-20 12:12:21.517086	venda_direta	pendente
231	27	107	1	6	f	fiado	2026-04-20 17:33:20.574081	venda_direta	pendente
232	30	101	1	8	f	fiado	2026-04-20 17:33:42.85257	venda_direta	pendente
233	18	108	1	7	t	transferencia	2026-04-20 17:41:48.57392	venda_direta	pago
235	25	110	1	7	f	fiado	2026-04-20 18:39:18.377149	venda_direta	pendente
236	17	56	1	7	f	fiado	2026-04-20 18:43:58.866551	venda_direta	pendente
237	21	111	1	7	f	fiado	2026-04-20 18:45:08.332509	venda_direta	pendente
238	24	109	1	7	f	fiado	2026-04-20 21:33:47.939418	venda_direta	pendente
\.


--
-- Name: caixa_id_seq; Type: SEQUENCE SET; Schema: public; Owner: bd_erp_cayube_user
--

SELECT pg_catalog.setval('public.caixa_id_seq', 1, false);


--
-- Name: cliente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: bd_erp_cayube_user
--

SELECT pg_catalog.setval('public.cliente_id_seq', 111, true);


--
-- Name: fechamento_caixa_id_seq; Type: SEQUENCE SET; Schema: public; Owner: bd_erp_cayube_user
--

SELECT pg_catalog.setval('public.fechamento_caixa_id_seq', 3, true);


--
-- Name: movimentacao_estoque_id_seq; Type: SEQUENCE SET; Schema: public; Owner: bd_erp_cayube_user
--

SELECT pg_catalog.setval('public.movimentacao_estoque_id_seq', 1, false);


--
-- Name: movimento_estoque_id_seq; Type: SEQUENCE SET; Schema: public; Owner: bd_erp_cayube_user
--

SELECT pg_catalog.setval('public.movimento_estoque_id_seq', 235, true);


--
-- Name: movimento_id_seq; Type: SEQUENCE SET; Schema: public; Owner: bd_erp_cayube_user
--

SELECT pg_catalog.setval('public.movimento_id_seq', 72, true);


--
-- Name: notificacao_id_seq; Type: SEQUENCE SET; Schema: public; Owner: bd_erp_cayube_user
--

SELECT pg_catalog.setval('public.notificacao_id_seq', 11, true);


--
-- Name: produto_id_seq; Type: SEQUENCE SET; Schema: public; Owner: bd_erp_cayube_user
--

SELECT pg_catalog.setval('public.produto_id_seq', 30, true);


--
-- Name: saldo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: bd_erp_cayube_user
--

SELECT pg_catalog.setval('public.saldo_id_seq', 1, true);


--
-- Name: usuario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: bd_erp_cayube_user
--

SELECT pg_catalog.setval('public.usuario_id_seq', 3, true);


--
-- Name: venda_id_seq; Type: SEQUENCE SET; Schema: public; Owner: bd_erp_cayube_user
--

SELECT pg_catalog.setval('public.venda_id_seq', 238, true);


--
-- Name: caixa caixa_pkey; Type: CONSTRAINT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.caixa
    ADD CONSTRAINT caixa_pkey PRIMARY KEY (id);


--
-- Name: cliente cliente_pkey; Type: CONSTRAINT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_pkey PRIMARY KEY (id);


--
-- Name: cliente cliente_telefone_key; Type: CONSTRAINT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_telefone_key UNIQUE (telefone);


--
-- Name: fechamento_caixa fechamento_caixa_pkey; Type: CONSTRAINT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.fechamento_caixa
    ADD CONSTRAINT fechamento_caixa_pkey PRIMARY KEY (id);


--
-- Name: movimentacao_estoque movimentacao_estoque_pkey; Type: CONSTRAINT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.movimentacao_estoque
    ADD CONSTRAINT movimentacao_estoque_pkey PRIMARY KEY (id);


--
-- Name: movimento_estoque movimento_estoque_pkey; Type: CONSTRAINT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.movimento_estoque
    ADD CONSTRAINT movimento_estoque_pkey PRIMARY KEY (id);


--
-- Name: movimento movimento_pkey; Type: CONSTRAINT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.movimento
    ADD CONSTRAINT movimento_pkey PRIMARY KEY (id);


--
-- Name: notificacao notificacao_pkey; Type: CONSTRAINT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.notificacao
    ADD CONSTRAINT notificacao_pkey PRIMARY KEY (id);


--
-- Name: produto produto_pkey; Type: CONSTRAINT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.produto
    ADD CONSTRAINT produto_pkey PRIMARY KEY (id);


--
-- Name: saldo saldo_pkey; Type: CONSTRAINT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.saldo
    ADD CONSTRAINT saldo_pkey PRIMARY KEY (id);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id);


--
-- Name: usuario usuario_usuario_key; Type: CONSTRAINT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_usuario_key UNIQUE (usuario);


--
-- Name: venda venda_pkey; Type: CONSTRAINT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.venda
    ADD CONSTRAINT venda_pkey PRIMARY KEY (id);


--
-- Name: movimento_estoque movimento_estoque_produto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.movimento_estoque
    ADD CONSTRAINT movimento_estoque_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produto(id);


--
-- Name: venda venda_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.venda
    ADD CONSTRAINT venda_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.cliente(id);


--
-- Name: venda venda_produto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: bd_erp_cayube_user
--

ALTER TABLE ONLY public.venda
    ADD CONSTRAINT venda_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produto(id);


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON SEQUENCES TO bd_erp_cayube_user;


--
-- Name: DEFAULT PRIVILEGES FOR TYPES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON TYPES TO bd_erp_cayube_user;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON FUNCTIONS TO bd_erp_cayube_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON TABLES TO bd_erp_cayube_user;


--
-- PostgreSQL database dump complete
--

\unrestrict aey5GQS5OREO0dJedSUEeEo2UsyEByLhkuzzYJdgaBRejtwSomlHFAUnxuKPGlK

