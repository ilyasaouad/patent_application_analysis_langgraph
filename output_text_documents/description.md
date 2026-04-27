## A Coexistence Device and a method for upgrading an optical line terminal

## Technical field

The present disclosure relates to a coexistence device and a method for upgrading an optical line terminal. More specifically, the disclosure relates to a coexistence device and a method for upgrading an optical line terminal as defined in the introductory parts of the independent claims.

## Background art

Optical line terminals (OLTs) are essential devices in modern fiber-optic networks, especially in passive optical networks (PONs). They serve as the service provider’s endpoint and perform two critical roles: first, they convert the electrical signals from the provider’s equipment into optical signals that can travel over the fiber network; second, they coordinate the multiplexing and management of data across multiple optical network units (ONUs) or optical network terminals (ONTs) that are installed at end-consumer premises.

An OLT handles both downstream traffic—from the OLT to consumer—and upstream traffic—from consumer back to the OLT—by employing specialized frame-processing mechanisms, wavelength division multiplexing (WDM) and or Time-division multiplexing (TDM), and media access control (MAC) protocols. These functions ensure that data is not only transmitted efficiently but also securely, often incorporating encryption or authentication measures to prevent unauthorized access between different ONTs.

In practical deployment, OLTs are often located either in centralized cabinets at an Internet Service Provider’s (OLT’s) facility or at local distribution points like apartment complexes or hotels. They are built to support various Passive Optical Network, PON, standards, such as GPON, EPON, XG-PON, and XGS-PON, accommodating different split ratios—typically 1:32, 1:64, or even up to 1:128—so that a single OLT port can serve many customer connections effectively. This scalability is crucial for delivering high-speed broadband to a large number of subscribers.

OLTs are critical not only for data transmission but also for maintaining the overall robustness and security of fiber-to-the-home (FTTH) networks and other fiber-based broadband deployments.

Upgrading Passive Optical Network (PON) standards comes with a range of technical, economic, and operational challenges. Some of the problems relates to:

1. Escalating Bandwidth Demands and Scalability: Modern applications such as 4K/8K streaming, cloud gaming, smart home connectivity, distance education, and remote work are pushing subscriber bandwidth requirements higher. Upgrading from legacy systems like GPON to next-generation solutions (e.g., XGS-PON, NG-PON2, or even 25G and beyond) means that networks must be designed to scale efficiently. This requires careful planning of split ratios and ensuring that the upgraded architecture remains flexible for future enhancements while accommodating increasing consumer densities and diverse service profiles.

2. Equipment Procurement and Vendor Lock-In: This vendor lock-in not only restricts customization and integration with other network components but also complicates the transition to more open, white-box technologies that can simplify upgrades while reducing costs. It is a problem that equipment cannot bridge old and new standards, particularly as operators balance the benefits of innovation against the constraints of existing infrastructure.

3. Technological Complexity and Compatibility Issues: Transitioning to next-generation PON standards often involves significant network re-engineering. It is a problem that backward compatibility with legacy systems (like GPON) may not be facilitated, and adds another layer of complexity, as networks must support a co-existence of technologies during the transition phase.

4. Economic Investment and Return on Investment (ROI): Upgrading PON standards is capital intensive. Investments are needed not only for new hardware and optical components but also for the design, testing, and integration of these systems into current networks. Operators need to balance the benefits of higher capacity and improved performance against the financial risks and ensure that the transition can deliver the expected returns over time.

5. Operational and Deployment Challenges: Upgrading a live network involves rigorous testing, minimal service disruption, and the ability to scale deployments rapidly—often in both greenfield and brownfield environments.

Ensuring backward compatibility during upgrades in Passive Optical Networks (PONs) involves a combination of robust standardization, smart hardware design, and strategic architectural planning commonly achieved by:

1. Adherence to Standardized Specifications: International standards bodies incorporate explicit requirements for backward compatibility in their recommendations.

2. Dual-Standard Operations and Flexible Hardware: Upgraded optical line terminals (OLTs) and optical network units (ONUs) are often built or updated to support dual-standard operations. This means they can operate with both the new high-speed protocols and the older legacy standards. This dual or multi standard capability allows network operators to serve customers with older equipment while gradually transitioning to newer technology, thereby protecting prior investments and minimizing service disruption.

3. Wavelength Division Multiplexing (WDM) and Segmented Architecture: A common tactic is to separate legacy and upgraded traffic by using different wavelengths within the same fiber infrastructure. By assigning distinct wavelengths for older and newer protocols, these systems can operate concurrently without interference. This setup allows service providers to upgrade segments of the network incrementally while ensuring that legacy devices continue to function reliably on their dedicated channels.

Greenfield refers to scenarios where the network is built from scratch. In a greenfield PON deployment, the infrastructure is designed and installed with the latest technology in mind.

Brownfield environments, in contrast, refer to upgrading or retrofitting an existing network. In a brownfield PON upgrade, operators work within an established infrastructure, striving to integrate new technology while maintaining service for current consumers. Key benefits include:

 Cost Efficiency and Utilization of Existing Assets: By leveraging the already deployed optical distribution network (ODN)—including fiber, splitters, and cabinets—operators can reduce the overall capital outlay. This is particularly attractive in mature markets where extensive fiber has already been installed.

 Minimized Disruption Through Incremental Upgrades: Brownfield upgrades often occur incrementally. For example, service providers can upgrade the central OLTs to support newer protocols (like migrating from GPON to XGS-PON) while still accommodating the legacy ONUs at customer premises. This phased approach can reduce service disruption and spread the investment over a longer period.

 Backward Compatibility: A critical component of brownfield upgrades is ensuring that new equipment can coexist seamlessly with legacy systems. Techniques such as dual-standard operation—that is, devices capable of handling both old and new standards concurrently—and wavelength division multiplexing (WDM) are frequently employed to manage the coexistence of different technology generations.

On the flip side, brownfield projects face several challenges:

 Legacy Constraints: Existing infrastructure may limit the potential capacity and performance improvements achievable through an upgrade. Physical limitations—such as outdated fiber types, connector standards, or constrained cabinet space—can restrict how much modern technology can be integrated.

 Complex Integration: Upgrading a live network means that operators must ensure complete backward compatibility. This complexity often requires advanced hardware (like dual-standard OLTs/ONUs) and extensive testing to minimize service interruptions during the transition phase. The need to maintain continuous service while modernizing parts of the network adds layers of technical and logistical challenges.

 Potential for Increased Maintenance: Retrofitting existing equipment alongside new systems can lead to operational inefficiencies. Balancing two generations of technology might complicate network management and troubleshooting, thereby increasing the need for specialized maintenance expertise.

There is thus a need for providing improved and simplified equipment for upgrading OLTs having less impact on the overall need for introducing advanced circuits on each port of the OLTs.

## Summary

It is an object of the present disclosure to mitigate, alleviate or eliminate one or more of the above-identified deficiencies and disadvantages in the prior art and solve at least the above-mentioned problems.

It is provided: a novel device for being integrated in for example in a Central Office, CO, Fiber Distribution Hub, FDH, connecting fiber-optic cables of the Core Network with the Last Mile Connection connecting consumers to OLT. These or similar passive Hub devices offer ports connecting the OLT side optical fiber lines with the consumer side optical fiber lines. Traditionally such ported optical fiber lines support one PON standard only, but lately two or more standards may be supported which may be transmitted on lines with dual or multi standard capabilities. New standards have higher capacity than Legacy standards, often double or more split ration capabilities. In order to filter and provide the new standards to the end customer, the FDHs must support the standards on all ports. Present disclosure describes how the new standard need only to be provided on a portion of the optical fiber lines connecting the Core Network with the Last Mile Connection, and still provide multiple standards to all Last Mile Connections.

According to a first aspect there is provided a Coexistence Device, Cex, for increasing the capabilities of an optical device, comprising:

- two or more first interfaces of the Cex for connecting to Optical Line Terminal, OLT, signal lines,

- a second interface of the Cex for connecting to a first Optical Distribution Network, ODN, signal line, and

- one or more third interfaces of the Cex for connecting to one or more corresponding second Optical Distribution Networks, ODN, signal line,

- a first optical filter configured for:

o passing through a first portion of a first filtered signal of a first frequency band from a first OLT signal on a first of the two or more first interfaces, and

o reflecting a second portion of the first filtered signal and a first signal from the first OLT signal on the first of the two or more first interfaces of the Cex on to the second interface of the Cex,

and

- one or more third optical filters configured for:

o receiving and passing from one or more corresponding second OLT signals from one or more corresponding second of the two or more first interfaces of the Cex of a second frequency band on to the third interface of the Cex.

The Cex is thus configured to support multiple, at least two, PON, standards, on one OLT line such as one Legacy standard such as GPON, and one or more further standards such as EPON, XG-PON, and XGS-PON, and further one or more Legacy PON standard only on one or more second OLT lines.

According to some embodiments the first portion of the first filtered signal is 100% of the first filtered signal, and the second portion of the first filtered signal is 0% of the first filtered signal. Optical filters may be configured to let a portion of a certain frequency band signal pass through the filter and reflecting the remaining portion. In the above-described aspect the filter is configured to let 100% of the certain frequency band signal pass through the filter, and 0% of the certain frequency band is reflected. All signals outside the certain frequency band will be reflected by the filter.

According to some embodiments, the Cex comprises:

- a splitter configured for splitting the first filtered signal on a first interface of the splitter into:

o a first split signal on a second interface of the splitter, and

o a second split signal on a third interface of the splitter,

- a second optical filter configured for:

o receiving and passing from the first signal being reflected by the first optical filter from the first OLT signal, a signal of the second frequency band, on to the second interface of the Cex, and

o receiving and reflecting the first split signal to the second interface of the Cex, and

- the third optical filter is further configured for:

o receiving and reflecting the second split signal on to the third interface of the Cex.

The advantage of this configuration is that the splitter will split the first filtered signal which typically has a bandwidth accommodating for at least two, four or more times the split ration of the signal of the second frequency band. Thus, the first filtered signal of the first frequency band from the first OLT signal on the first of the two or more first interfaces will now be passed on to both the first and second ODN signal lines via the second and third optical filters respectively.

According to some embodiments, the second and third optical filters are configured to reflect signals of the first frequency band from the second and third interfaces of the Cex respectively on to the second interface and the third interface of the splitter respectively, and the splitter is configured to pass the reflected signals on to the first interface of the splitter and on to the first of the two or more first interfaces via the first optical filter.

This means that ODN signals of the first frequency band from both ODN signal lines are forwarded to the first of the two or more first interfaces via the first optical filter by the splitter and onto the first OLT signal line.

According to some embodiments, the second optical filter is further configured to pass signals of the second frequency band from the second interface of the Cex, and further reflect these signals by the first optical filter to the first of the two or more first interfaces of the Cex.

Thus, the signals returning on the first ODN line of the second frequency band is transmitted onto the first OLT signal line, the first of the two or more first interfaces.

According to some embodiments, the third optical filter is further configured to pass signals of the second frequency band from the third interface of the Cex, on to the second of the two or more first interfaces of the Cex.

Thus, the signals returning on the second ODN line of the second frequency band is transmitted onto the second OLT signal line, the second of the two or more first interfaces.

According to some embodiments, the Cex is arranged in two separate units wherein:

the first Cex unit comprise:

o the first of the two or more first interfaces,

o the splitter,

o the second interface of the Cex, and

o the first and second optical filter,

## and

the second portion of the Cex the Cex comprises:

o the second of the two or more first interfaces,

o the third interface of the Cex, and

o the third optical filter,

the first Cex unit further comprising a first intermediate interface on the OLT side, and the second split signal is connected to the first intermediate interface, and

the second Cex unit further comprising a second intermediate interface on the OLT side being connected to the ODN side of the third optical filter.

Splitting the device in two modules, one for each port, may advantageous since the function of the third optical filter may then be used for other applications and configurations.

According to some embodiments, the Cex comprises: a connector for connecting the first intermediate interface and the second intermediate interface.

The first and second unit is connected to provide the functions described above.

According to some embodiments, the Cex further comprises:

- a fourth optical filter configured for:

o passing a third OLT signal of a third frequency band on a third of the two or more first interfaces of the Cex and connecting to the splitter side of the first optical filter reflecting it to the first interface of the splitter,

- the splitter is configured for splitting the third OLT signal into the first split signal and the second split signal on the second interface and the third interface of the splitter respectively.

This means that the same basic technology may support multiple standards wherein new standards need only be transmitted on half of the optical lines leading to the FDHs. All those multiple standards will be provided for all the consumers via a 1-2 splitter.

According to some embodiments, the second and third optical filters are configured to reflect signals of the third frequency band from the second and third interfaces of the Cex on to the second interface and the third interface of the splitter respectively, and the splitter is configured to pass the reflected signals on the first interface of the splitter and reflecting the signals of the third frequency band from the first optical filter and the fourth optical filter passing this signal onto the third of the two or more first interfaces of the Cex.

Thus, all frequency bands are supported from ODN side to OLT side of the FDHs.

According to some embodiments,

the fourth optical filter is further configured for:

o reflecting a fourth OLT signal of a fourth frequency band on a fourth of the two or more first interfaces of the Cex to the splitter side of the first optical filter reflecting it to the first interface of the splitter,

and

the splitter is configured for splitting the fourth OLT signal on to the second and third interface of the splitter respectively.

Thus, adding further OLT signal lines supporting even further frequency band to the 1- 2 splitter configuration is facilitated.

According to some embodiments,

the second and third optical filters are configured to reflect signals of the fourth frequency band from the second and third interfaces of the Cex on to the second interface and the third interface of the splitter respectively, and

the splitter is configured to pass the reflected signals of the fourth frequency band on the first interface of the splitter and reflecting the signals of the fourth frequency band from the first optical filter via the fourth optical filter and onto the fourth of the two or more first interfaces of the Cex

According to some embodiments, the Cex comprises:

o a third of the two or more first interfaces of the Cex configured for: passing through, to a fourth interface of the splitter, a third OLT signal of a third frequency band on the third of the two or more first interfaces, and

o the splitter is configured for splitting the third OLT signal into the first split signal and the second split signal on the second interface and the third interface of the splitter respectively.

This means that the same basic technology may support multiple standards wherein new standards need only be transmitted on half of the optical lines leading to the FDHs. All those multiple standards will be provided for all the consumers via a 2-2 splitter.

According to some embodiments, the second and third optical filters are configured to reflect signals of the third frequency band from the second and third interfaces of the Cex on to the second interface and the third interface of the splitter respectively, and the splitter is configured to pass the reflected signals on the fourth interface of the splitter and onto the third of the two or more first interfaces of the Cex.

Thus, all standards also are supported from ODN side to OLT side of the FDHs.

According to some embodiments, the Cex comprises:

- a fourth optical filter configured for:

o passing the third OLT signal of the third frequency band on to the fourth interface of the splitter,

o reflecting a fourth OLT signal of a fourth frequency band on a fourth of the two or more first interfaces of the Cex to the fourth interface of the splitter, and

o the splitter is configured for splitting the third frequency band on to the second and third interface of the splitter respectively.

According to some embodiments, the splitter is configured to pass the reflected signals of the third frequency band on to the fourth interface of the splitter and onto the fourth of the two or more first interfaces of the Cex via the fourth optical filter.

Then, there is support for future PON standards using both 2-1 and 2-2 splitters.

According to some embodiments, the Cex further comprising:

- further one or more optical filters configured for:

o passing through one or more further filtered signals of further frequency bands from further OLT signals on one or more further of the two or more first interfaces of the Cex, and

o reflecting even further signals from even further OLT signals on even further interfaces of the one or more first interfaces of the Cex, and

o the splitter is configured for passing the further frequency bands on the second interface and the third interface of the splitter respectively.

According to some embodiments, the second and third optical filters are configured to reflect signals of one or more of the further frequency bands from the second and third interfaces of the Cex respectively on to the second interface and the third interface of the splitter respectively, and

the splitter is configured to pass the reflected signals on to the first interface or fourth interface respectively of the splitter and to the first of the further two or more first interfaces of the Cex via the further one or more optical filters.

According to some embodiments, the one or more optical filters are configured to reflect:

- the further frequency band of the passed signal to the further interfaces of the two or more first interfaces of the Cex, and/or

- the even further frequency bands of the further of the passed signal to the even further interfaces of the two or more first interfaces of the Cex.

Thus, support for cascading of multiple POPN standards are provided.

According to some embodiments, the first frequency band is an XGS band.

According to some embodiments, the first signal is a GPON signal.

According to some embodiments, the second signal is a GPON signal.

According to some embodiments, the first of the one or more first interface is an XGS/GPON Combo port.

According to some embodiments, the third of the one or more first interfaces is a 25G/50G OLT Port.

According to some embodiments, the fourth of the one or more first interfaces is a UPG port.

It is within the concept of present disclosure to support any future PON standard, and this may be provided by customizing the optical filters.

According to a second aspect there is provided a method for upgrading an Optical Line Terminal, OLT, combining two or more signal standards, the method comprising the steps:

providing an OLT comprising two or more ports supporting a first of two or more Passive Optical Network, PON, standards, and at least two PON signal lines being connected to the PON side of the two or more ports, the two or more ports of the OLT further connects to a first and second Optical Distribution Network, ODN, signal lines on the ODN side of the two or more ports, and

replacing one or more of any of the first of every second of the ports with a Cex according to the first aspect.

The method supporting all standards on every two optical lines on the ODN port side but requiring only the Legacy standard on both corresponding optical lines on the OLT port side. At the same time all non-legacy standards will need to be supported only on one of the optical lines on the OLT port side.

According to some embodiments, the method comprises the step:

replacing the first of the at least two PON lines with a PON line providing a combination of a first of two or more standards and a second of the two or more standards,

connecting the PON line with the combination of the first of two or more standards to the first of the two or more first interfaces of the Cex,

disconnecting the second of the at least two PON lines and connecting it to the second of the two or more first interfaces of the Cex.

reconnecting the first and second ODN lines to the second interface of the Cex and the third interface of the Cex respectively, and when the Cex is a Cex according to : o connecting the first intermediate interface of the first Cex unit with the second intermediate interface of the second Cex unit.

The method provides for a simplified process to upgrade the optical network with minimized fault risk and low cost.

According to some embodiments, the method comprises the further step:

- connecting a PON line of a third of the two or more standards on the third of the two or more first interfaces of the Cex.

According to some embodiments, the method comprises the further step:

- connecting a PON lines of a fourth of the two or more standards on the fourth of the two or more first interfaces of the Cex.

According to some embodiments, the method comprises the step:

- connecting a PON lines of a further of the two or more standards on the further of the two or more first interfaces of the Cex, and/or

- connecting a PON lines of an even further of the two or more standards on the even further of the two or more first interfaces of the Cex.

Effects and features of the second aspect are to a large extent analogous to those described above in connection with the first aspect. Embodiments mentioned in relation to the first aspect are largely compatible with the second aspect.

The present disclosure will become apparent from the detailed description given below. The detailed description and specific examples disclose preferred embodiments of the disclosure by way of illustration only. Those skilled in the art understand from guidance in the detailed description that changes and modifications may be made within the scope of the disclosure.

Hence, it is to be understood that the herein disclosed disclosure is not limited to the particular component parts of the device described or steps of the methods described since such device and method may vary. It is also to be understood that the terminology used herein is for purpose of describing particular embodiments only, and is not intended to be limiting. It should be noted that, as used in the specification and the appended claim, the articles "a", "an", "the", and "said" are intended to mean that there are one or more of the elements unless the context explicitly dictates otherwise. Thus, for example, reference to "a unit" or "the unit" may include several devices, and the like. Furthermore, the words "comprising", "including", "containing" and similar wordings does not exclude other elements or steps.

Terminology

The term "PON”, is to be interpreted as Passive Optical Network

The term "GPON”, is to be interpreted as Gigabyte Passive Optical Network ….

The term "Cex”, is to be interpreted as Coexistence Element

The term "ODN”, is to be interpreted as Optical Distribution Network

The term "OLT”, is to be interpreted as Optical Line Termination , and is also what is often called optical line terminal.

The term "ONU”, is to be interpreted as Optical Network Unit (consumer side unit or terminal on client side)

The term "ODF”, is to be interpreted as Optical Distribution Frame

The term "OTDR”, is to be interpreted as Optical Time Domain Reflectometry

The term "UPG port”, is to be interpreted as Upgrade port

The term "TWDM”, is to be interpreted as Time and Wavelength Division Multiplexing

The term "FTTH/B/P”, is to be interpreted as Fiber To The Home/Building/Plant

The term "XG-PON”, is to be interpreted as Gigabit-capable Passive Optical Network

The term "XGS-PON”, is to be interpreted as Gigabit Symmetrical Passive Optical

The term "Legacy standard" is to be interpreted as the original PON standard of the system, which is to be upgraded.

The term "OLT side" is to be interpreted as any network upstream of the Cex.

The term “consumer side” is to be interpreted as any network downstream of the Cex.

Brief descriptions of the drawings

The above objects, as well as additional objects, features and advantages of the present disclosure, will be more fully appreciated by reference to the following illustrative and nonlimiting detailed description of example embodiments of the present disclosure, when taken in conjunction with the accompanying drawings.

Figure “PRIOR ART 1” show an overview of a typical optical fiber network from an internet provider network to an end consumer Optical network unit.

Figure “PRIOR ART $2 ^ { \prime \prime }$ shows the layout of a traditional Optical Fiber Distribution Hub.

Figure 1 shows device of present disclosure substituting every second port of the Optical Fiber Hub shown in “PRIOR ART $2 ^ { \prime \prime }$ figure.

Figure 2A shows an embodiment of the device according to the present disclosure comprising a 1-2 splitter, wherein one of every second port to the OLT side being a combo port, supporting at least two PON standards on the optical fiber line connecting to the combo port of which one Is a Legacy standard, and the second port to the OLT side support only the Legacy standard.

Figure 2B shows an embodiment of the device according to the embodiment of figure 2A comprising further cascade coupled optical fiber line connections supporting even further PON standards.

Figure 2C shows an embodiment of the device according to the present disclosure comprising a 2-2 splitter, wherein one of every second port to the OLT side being a combo port, supporting at least two PON standards on the optical fiber line connecting to the combo port, and a third connecting port on the OLT side for connecting to a further PON standard.

Figure 2D shows an embodiment of the device according to the embodiment of figure 2C comprising further cascade coupled fiber line connections supporting even further PON standards.

Figure 2E shows an embodiment of the device according to the embodiment of figure 2D comprising even further cascade coupled fiber line connections supporting even further PON standards.

Figure 2F shows an embodiment of the device according to the present disclosure wherein the splitter is substituted by a partial reflecting filter.

Figure 2G shows an embodiment of the device according to the embodiment of figure 2A wherein the device is spitted in a first and a second portion.

Figure 2H shows an embodiment of the device according to the embodiment of figure 2A, wherein every third port is substituted by a combo port, and the device supports two ports connected to Legacy only optical lines on the OLT side.

Figure 3A shows traditional rack upgrade in an optical network

Figure 3B shows how the present disclosure enables supporting all users with dual PON standards without replacing more than every second OLT.

Figure 3C shows how the present disclosure supports future upgrade policies.

Figure 3D shows a typical upgrade scenario from 2x32 split GPON to GPON & XGS PON to all 64 consumers with XGSPON on only one Combo port.

Figure 3E shows device of present disclosure connecting to GPON + Combo port.

Figure 3F shows device of present disclosure connecting to GPON + Combo port + 50G.

Figure 3G shows device of present disclosure connecting to 2x (GPON + Combo port) + 50G.

Figure 4A shows the diagram of an optical filter with dual input line (input and reflected port) and one pass port.

Figure 4B show an actual component according to figure 4A.

## Detailed description

The present disclosure will now be described with reference to the accompanying drawings, in which preferred example embodiments of the disclosure are shown. The disclosure may, however, be embodied in other forms and should not be construed as limited to the herein disclosed embodiments. The disclosed embodiments are provided to fully convey the scope of the disclosure to the skilled person.

The first aspect of this disclosure, shown in figure 2A and optional in figure 2H, shows a Coexistence Device 1,1’,2,3,4, ,6,6’, Cex, for increasing the capabilities of an optical device, comprising:

- two or more first interfaces 11,31,51,52 of the Cex for connecting to Optical Line Terminal, OLT, signal lines,

- a second interface 21,61 of the Cex for connecting to a first Optical Distribution Network, ODN, signal line, and

- one or more third interfaces 41,42,71 of the Cex for connecting to one or more corresponding second Optical Distribution Networks, ODN, signal line,

- a first optical filter ,302 configured for:

o passing through a first portion of a first filtered signal 110 of a first frequency band from a first OLT signal 108 on a first of the two or more first interfaces 11, and

o reflecting a second portion of the first filtered signal 310 and a first signal 101,301 from the first OLT signal 108 on the first of the two or more first interfaces 11 of the Cex on to the second interface 21,61 of the Cex,

and

- one or more third optical filter , ’, ,90 configured for:

o receiving and passing from one or more second OLT signals 113,123 from one or more corresponding second of the two or more first interfaces 31,32 of the Cex of a second frequency band on to the one or more corresponding third interfaces 41,42,71 of the Cex.

For the purpose of understanding the embodiments shown in present disclosure it shall be considered a scenario where the Legacy standard is a GPON standard, and a combo port supports two standards, typically GPON and XGS-PON, on the same dual standard line. Further standards may support 50G PON, and UPG or OTDR standards. GPON technology typically handles distribution coefficients up to 1:64 with maximum 1:128. Newer standards, such as XGS-PON technology typically handle the distribution coefficient of 1:128, with a maximum of 1:256. The embodiments shown in figure 3D, figure 3E, figure 3F, and figure 3G provides GPON standard lines at a distribution coefficient of 1:32, XGS-PON standard lines at a distribution

coefficient of 1:64, and 50G standard lines at a distribution coefficient of, at least, 1:128. When upgrading a system from GPON to XGS-PON, it may be desirable to offer this feature to all consumers of the network, but upgrading all ports downstream in the network may be slow. Present disclosure requires for example only half or one third of the network to be upgraded, and at the same time will all connected PON standards be offered to the consumers. This both ensures a quicker rollout, spending fewer resources, and provides better backward compatibility since all consumers may benefit from the LEGACY standard being supported together with an upgraded standard. The figures are indifferent as to which PON standard is used as the system can just as well be used when upgrading the ODN from an XGS-PON standard to a 50G PON standard, where the XGS-PON will be the Legacy standard supported by all Optical lines through the Cex.

Figure 2A show a setup where one Legacy standard lines are passed through the Cex, and one line is a combo standard line.

In both setups there is comprised a splitter 100,200 for spreading the upgrade standard to all consumer lines.

There is also envisaged as shown in figure 2F an embodiment for achieving the same feature, without using a splitter 100, 200,. A reflective optical filter 302 substitutes the splitter. The reflective optical filter is configured to let a certain percentage of the filtered light frequency pass and reflect the rest portion of that light frequency. Typically, will % of for example the XGS-PON light pass, and % of the XGS-PON light will be reflected together with the rest of the light frequencies.

For the purpose of encompass both the embodiments comprising a splitter and the reflective optical filter, the first optical filter is a traditional optical filter described as an optical filter wherein light of a certain frequency band is passed and all other light frequencies are reflected. Thus, in these embodiments the first optical filter is descried as a filter wherein the first portion of the first filtered signal 110 is 100% of the first frequency band 108, and the second portion of the first filtered signal 110 is 0% of the first frequency band 108.

The Cex comprises:

- a splitter 100,200 configured for splitting the first filtered signal 110 on a first interface 201 of the splitter 100,200 into:

o a first split signal 111,114 on a second interface 202 of the splitter 100,200, and

o a second split signal 112,115 on a third interface 203 of the splitter 100,200,

- a second optical filter , configured for:

o receiving and passing from the first signal 101 being reflected by the first optical filter from the first OLT signal 108, a signal of the second frequency band, on to the second interface 21,61 of the Cex, and

o receiving and reflecting the first split signal 111,114 to the second interface 21,61 of the Cex,

and

- the third optical filter , is further configured for:

o receiving and reflecting the second split signal 112,115 on to the third interface 41,71 of the Cex.

Looking at figure 2A with the default PON standard setup as discussed above this translates to that the splitter receives from the OLT side an XGS-PON standard signal on the combo port line through the first optical filter. This filtered XGS-PON signal is split ( % light each), into the first and second split signal, each being output to corresponding second and third 202, 203 interface of the consumer side of the splitter.

The GPON signal from the combo port line is reflected by the XGS-PON filter on the OLT side of the splitter and transmitted to the second optical filter , which is a GPON filter. The GPON signal is passed through this second optical filter ,60. At the same time is the consumer side of the second optical filter connected to the second interface 21, 61 of the Cex consumer side being connected to a first group of consumers. The second interface 202 of the consumer side of the splitter is also connected to the consumer side of the second optical filter, and the second optical filter is reflecting the first split signal 111, 114 to the second interface 21, 61 of the Cex.

At the same time the third optical filter , is a GPON filter which pass the GPON signal, , called the second OLT signal 113, present on the optical line connected to the second 31 of the first interfaces, the second of the OLT side lines, to the third interface 41 of the Cex. The consumer side of the third optical filter is further connected to the second split signal 112, 115 to the third interface 41 of the Cex being connected to a second group of consumers.

Now both GPON and XGS-PON standards are distributed to all consumers.

The second , and third , optical filters are configured to reflect signals 111,112,114,115 of the first frequency band from the second 21,61 and third 41,71 interfaces of the Cex respectively on to the second interface 202 and the third interface 203 of the splitter 100,200 respectively, and the splitter 100,200 is configured to pass the reflected signals 111,112,114,115 on to the first interface 201 of the splitter 100,200 and on to the first of the two or more first interfaces 11 of the Cex via the first optical filter 10.

This way ensures that, in the example scenario, that any XGS-PON signal transmitted from the consumer side of the Cex is reflected to be transmitted back to the dual standard optical line on the OLT side of the Cex. It shall be noted that although the optical signals may be split downstream through the splitter 100, 200. But, light from different consumers cannot be combined on the OLT side of the Cex. Light with the same wavelength mixes and cannot be separated in any good way. Therefore, there is a special protocol in PON, TDM (time division multiplexing). Each upstream signal (i.e. ODN to OLT) gets a time slot to send its signal within, then the light is not mixed.

The second , optical filter is further configured to pass signals of the second frequency band 101 from the second interface 21,61 of the Cex, and further reflect these signals by the first optical filter to the first of the two or more first interfaces 11 of the Cex.

Thus, the GPON signal from the first group of consumers are transmitted to the dual standard line on the OLT side of the Cex.

The third , optical filter is further configured to pass signals of the second frequency band 113from the third interface 41,71 of the Cex, on to the second of the two or more first interfaces 31 of the Cex.

Thus, the GPON signal from the second group of consumers are transmitted to the Legacy standard line on the OLT side of the Cex.

As shown in the present disclosure, in accordance with figure 2B, it should be understood that the further OLT signal lines 119, m, n… shown there also may be implemented as further OLT signal lines in accordance with figure 2F. These lines and optical filters are not shown in figure 2F but could be cascade coupled via optical filters to the first OLT signal 108 line in a similar way as explained in figure 2B and 2E.

For some purposes there may be advantageous to split the Legacy line components of the Cex, and the Combo standard line components of the Cex in two separate units as shown in figure 2G. The second split signal on the consumer side of the splitter is then connected to a port connector on both uni ${ \boldsymbol { \cdot } } { \mathsf { s } } ,$ such that if they are to operate together as depicted in Fig 2A, a connecting line must be connected to the port connectors. The two units may be operated as independent circuits.

The Cex is arranged in two separate units $6 , 6 ^ { \prime }$ wherein:

the first Cex unit 6 comprise:

o the first of the two or more first interfaces 11,

o the splitter 100,200,

o the second interface 21,61 of the Cex, and

o the first and second optical filter , ,

and

the second portion of the Cex comprises:

o the second of the two or more first interfaces 31,

o the third interface 41,71 of the Cex, and

o the third 90 optical filter,

the first Cex unit 6 further comprises a first intermediate interface 81 on the OLT side, and the second split signal 112,115 is connected to the first intermediate interface 81, and the second Cex unit ${ \boldsymbol { 6 } } ^ { \prime }$ further the Cex comprises a second intermediate interface 82 on the OLT side being connected to the ODN side of the third optical filter 90.

As shown in the present disclosure, in accordance with figure 2B, it should be understood that the further OLT signal lines 119, m, n… shown there also may be implemented as further OLT signal lines in accordance with figure 2G. These lines and optical filters are not shown in figure 2G but could be cascade coupled via optical filters to the first OLT signal 108 line in a similar way as explained in figure 2B and 2E.

The Cex comprises: a connector 83 for connecting the first intermediate interface 81 and the second intermediate interface 82.

In the following more complex scenarios wherein the dual standard optical line is cascade connected with one or more further OLT side lines. All being combined in one or more interfaces to the OLT side of the splitter. The splitter being either a 1-2, 1-3, 2-2 or other configuration. Cascade coupling OLT side lines may accommodate for future PON standards and for example support all GPON, XGS-PON, and 50G to all consumer groups.

The scenario described in figure 2B:

The Cex comprises:

- a fourth optical filter configured for:

o passing a third OLT signal 109 of a third frequency band on a third of the two or more first interfaces 51 of the Cex and connecting to the splitter 100side of the first optical filter reflecting it to the first interface 201 of the splitter 100,

the splitter 100,200 is configured for splitting the third OLT signal 109 into the first split signal 111’ and the second split signal 112’ on the second interface 202 and the third interface 203 of the splitter 100respectively.

The second and third optical filters are configured to reflect signals 111’,112’ of the third frequency band from the second 21 and third 41 interfaces of the Cex on to the second interface 202 and the third interface 203 of the splitter 100,200 respectively, and

the splitter 200 is configured to pass the reflected signals 111’,112’ on the first interface 201 of the splitter 100and reflecting the signals 111’,112’ of the third frequency band from the first optical filter ,302 and the fourth optical filter passing this signal onto the third of the two or more first interfaces 51 of the Cex.

The fourth optical filter is further configured for:

reflecting a fourth OLT signal 119 of a fourth frequency band on a fourth of the two or more first interfaces 52 of the Cex to the splitter 100side of the first optical filter reflecting it to the first interface 201 of the splitter 100,

## and

the splitter 100is configured for splitting the fourth OLT signal 119 on to the second 202 and third interface 203 of the splitter 100respectively.

The second and third optical filters are configured to reflect signals 111’, 112’ of the fourth frequency band from the second 21 and third 41 interfaces of the Cex on to the second interface 202 and the third interface 203 of the splitter 100, respectively, and

the splitter 100 is configured to pass the reflected signals 111’,112’ of the fourth frequency band on the first interface 201 of the splitter 100and reflecting the signals 111’,112’ of the fourth frequency band from the first optical filter ,302 via the fourth optical filter and onto the fourth of the two or more first interfaces 52 of the Cex.

As shown in the present disclosure, in accordance with the splitter 200 of figure 2E, it should be understood that the further OLT signal lines m, n… shown there also may be implemented as further OLT signal lines in accordance with figure 2B. These lines and optical filters are not shown in figure 2B but could be cascade coupled via optical filters to the fourth OLT signal 119 line in a similar way as explained in figure 2E.

The scenario described in figure 2C, figure 2D, and figure 2E:

Further, the Cex comprises:

a third of the two or more first interfaces 51 of the Cex configured for: passing through, to a fourth interface 204 of the splitter 200, a third OLT signal 109 of a third frequency band on the third of the two or more first interfaces 51, and

the splitter 200 is configured for splitting the third OLT signal 109 into the first split signal 114 and the second split signal 115 on the second interface 202 and the third interface 203 of the splitter 200 respectively.

The second and third optical filters are configured to reflect signals 114,115 of the third frequency band from the second 61 and third 71 interfaces of the Cex on to the second interface 202 and the third interface 203 of the splitter 200 respectively, and

the splitter 200 is configured to pass the reflected signals 114,115 on the fourth interface 204 of the splitter 200 and onto the third 109 of the two or more first interfaces 51 of the Cex.

The Cex comprises:

- a fourth optical filter configured for:

o passing the third OLT signal 109 of the third frequency band on to the fourth interface 204 of the splitter 200,

o reflecting a fourth OLT signal 119 of a fourth frequency band on a fourth of the two or more first interfaces 52 of the Cex to the fourth interface 204 of the splitter 200, and

o the splitter 200 is configured for splitting the third frequency band 119 on to the second 202 and third interface 203 of the splitter 200 respectively.

The splitter 200 is configured to pass the reflected signals 114,115 of the third frequency band on to the fourth interface 204 of the splitter 200 and onto the fourth of the two or more first interfaces 52 of the Cex via the fourth optical filter 50.

The Cex comprises:

- further one or more optical filters 50m,50n configured for:

o passing through one or more further filtered signals of further frequency bands from further OLT signals $\mathsf { m } , \ldots$ . on one or more further of the two or more first interfaces 51a of the Cex, and

o reflecting even further signals from even further OLT signals $\mathsf { n } , \ldots$ on even further interfaces of the one or more first interfaces 52a of the Cex, and

o the splitter 200 is configured for passing the further frequency bands on the second interface 202 and the third interface 203 of the splitter 200 respectively.

The second and third optical filters are configured to reflect signals 114,115 of one or more of the further frequency bands from the second 61 and third 71 interfaces of the Cex respectively on to the second interface 202 and the third interface 203 of the splitter 200 respectively, and

the splitter 200 is configured to pass the reflected signals 114,115 on to the fourth interface 204 of the splitter 200 and to the first of the further two or more first interfaces 51a of the Cex via the further one or more optical filters 50m,50n.

The one or more optical filters 50m,50n are configured to reflect:

- the further frequency band of the passed signal to the further interfaces of the two or more first interfaces 51a of the Cex, and/or

- the even further frequency bands of the further of the passed signal to the even further interfaces of the two or more first interfaces 52a of the Cex.

Figure 2H show a setup where three OLT side lines 108, 113, 123 of which two OLT lines 113, 123 are passed through the Cex, and one OLT side line 108 is a combo line. A first optical frequency band 110 signal of the combo line 108 is passed through the first optical filter , and the splitter splits the first optical frequency band 110 signal into three 111, 112, 114 portions of the first optical frequency band 110. Each portion is reflected via the three optical filters , , ’ respectively on the consumer side of the splitter to be reflected out to the second 21 and two third interfaces 41, 42 respectively of the Cex. Further OLT lines, equal to the first two OLT lines 113, 123 may be added to the Cex with corresponding splitter portions connected through further filters ’. In such a case with further OLT lines, the splitter split the first optical frequency band 110 signal of the combo line 108 into number of portions equal to the OLT side lines connected to the Cex.

It should be understood that each of the embodiments shown in figure 2A – 2E and figure 2G, the splitter comprised may be configured to split the first optical frequency band 110 signal of the combo line 108, and any further frequency bands 119, m, n, present on the first interface (201) of the splitter (100,200) and /or the into more than two portions, mirroring the number of OLT side lines connected to the Cex, and each portion is reflected into each consumer side line.

As shown in the present disclosure, in accordance with the splitter 200 of figure 2E, it should be understood that the further OLT signal lines m, n… shown there also may be implemented as further OLT signal lines in accordance with figure 2H. These lines and optical filters are not shown in figure 2H but could be cascade coupled via optical filters to the fourth OLT signal 119 line in a similar way as explained in figure 2E.

The first frequency band 110 is an XGS band.

The first signal 101 is a GPON signal.

The second signal 113 is a GPON signal.

The first of the one or more first interface 11 is an XGS/GPON Combo port.

The third of the one or more first interfaces 51 is a 25G/50G OLT Port.

The fourth of the one or more first interfaces 52 is a UPG port.

Figure 3D, and figure 3E, shows how the Cex could be implemented between the OLT and the consumer to increase the functionality of all consumers in the network to a dual standard operation in the network supporting both GPON and XGS PON standards. This is accomplished by: upgrading from a 2x32 split GPON scenario only one of the OLT lines to a combo line, where one OLT line is upgraded to the combo line carrying both a 32 split GPON line and a 64 split XGS PON line. A Cex in accordance with figure 2A is introduced to enable all 64 consumers of the previous 2x32 split GPON scenario get access to both GPON and XGS PON lines.

Figure 3F shows a scenario where the Cex in figure 3D is substituted by a Cex in accordance with figure 2B or figure 2C to increase the functionality of all consumers in the network to a multiple standard operation in the network supporting GPON, XGS PON and 50G standards. This is accomplished by: upgrading from a 2x32 split GPON scenario only one of the OLT lines to a combo line, where one OLT line is upgraded to the combo line carrying both a 32 split GPON line and a 64 split XGS PON line. Then, introducing a third OLT line supporting the 50G standard, and the Cex in accordance with figure 2B or figure 2C enables all 64 consumers of the previous 2x32 split GPON scenario to get access to GPON, XGS PON, and 50G standard lines.

As shown in Figure 3F, the Cex described in the present disclosure can be expanded to include multiple additional standard lines 119, m, n… . This is illustrated in figure 2B, figure 2D and figure 2E wherein all standards are made available for all consumers connected to the consumer side of the Cex. In this way the Cex may provide for future expansion of the OLT side of the network wherein all the consumers are secured access to these future standards without relying on upgrades of the complete network.

Figure 3G shows a scenario where two of the Cex in accordance with figure 3D is substituted by two Cex in accordance with figure 2B or figure 2C to increase the functionality of all consumers in the network to a multiple standard operation in the network supporting GPON, XGS PON and 50G standards. Since the 50G line typically splits to 128 or more, each Cex need only half or less of the 50G standard line to serve all the 64 consumers of each of the 2xGPON consumers. Therefore, to serve 128 consumers it is sufficient to upgrade the network with only one 50G standard line for each two or more Cex as described in accordance with figure 3F. By splitting the 50G standard line in two upstream of two Cexs, each half may be connected as the third OLT signal 109 to each of the two Cexs respectively. This enables all 128 consumers of the previous 4x32 split GPON scenario to get access to GPON, XGS PON, and 50G standard lines.

The second aspect of this disclosure shows a method for upgrading an Optical Line Terminal, OLT, combining two or more signal standards, the method comprising the steps:

providing an OLT comprising two or more ports supporting a first of two or more Passive Optical Network, PON, standards, and at least two PON signal lines being connected to the PON side of the two or more ports, the two or more ports of the OLT further connects to a first and second Optical Distribution Network, ODN, signal lines on the ODN side of the two or more ports, and

- replacing one or more of any of the first of every second of the ports with a Cex 1,2,3,4,6,6’ according to the first aspectto 21.

The method comprises the step:

o replacing the first of the at least two PON lines with a PON line providing a combination of a first of two or more standards and a second of the two or more standards,

o connecting the PON line with the combination of the first of two or more standards to the first of the two or more first interfaces 11 of the Cex,

o disconnecting the second of the at least two PON lines and connecting it to the second of the two or more first interfaces 31 of the Cex.

o reconnecting the first and second ODN lines to the second interface 21,61 of the Cex and the third interface 41,71 of the Cex respectively,

and when the Cex is a Cex $6 { , } 6 { ^ \prime }$ according to:

o connecting the first intermediate interface 51 of the first Cex unit 6 with the second intermediate interface 61 of the second Cex unit 6’.

The method further comprises the step:

- connecting a PON line of a third of the two or more standards on the third of the two or more first interfaces 51 of the Cex.

The Cex 1,2,3,4 is a Cex 1,2,3,4 according to the first aspect is, and the method further the method comprises the step: -

connecting a PON lines of a fourth of the two or more standards on the fourth of the two or more first interfaces 52 of the Cex.

The method comprises the step:

- connecting a PON lines of a further of the two or more standards on the further of the two or more first interfaces 51a of the Cex, and/or

- connecting a PON lines of an even further of the two or more standards on the even further of the two or more first interfaces 52b of the Cex.

The person skilled in the art realizes that the present disclosure is not limited to the preferred embodiments described above. The person skilled in the art further realizes that modifications and variations are possible within the scope of the appended claims. Additionally, variations to the disclosed embodiments can be understood and effected by the skilled person in practicing the claimed disclosure, from a study of the drawings, the disclosure, and the appended claims.